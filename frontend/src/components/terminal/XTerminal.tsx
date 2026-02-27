import { useEffect, useRef } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebglAddon } from "@xterm/addon-webgl";
import { XTERM_THEME } from "../../constants/theme";
import { useTerminalStore } from "../../stores/terminalStore";
import "@xterm/xterm/css/xterm.css";

interface XTerminalProps {
  sessionId: string;
  visible: boolean;
  initCommand?: string;
  onSendReady?: (sendFn: (message: string) => void) => void;
}

export function XTerminal({ sessionId, visible, initCommand, onSendReady }: XTerminalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const visibleRef = useRef(visible);
  visibleRef.current = visible;
  const setSessionConnected = useTerminalStore((s) => s.setSessionConnected);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;

    const term = new Terminal({
      theme: XTERM_THEME,
      fontFamily: "JetBrains Mono, Fira Code, monospace",
      fontSize: 13,
      lineHeight: 1.4,
      cursorBlink: true,
      cursorStyle: "bar",
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);

    // Open immediately so the terminal can buffer incoming data
    term.open(container);

    termRef.current = term;
    fitAddonRef.current = fitAddon;

    // Intercept Shift+Enter at the DOM level (capture phase, before xterm
    // processes it) and send CSI u escape sequence so CLI tools like Claude
    // Code can distinguish it from plain Enter (newline vs submit).
    const handleShiftEnter = (ev: KeyboardEvent) => {
      if (ev.key === "Enter" && ev.shiftKey && !ev.metaKey && !ev.ctrlKey) {
        ev.preventDefault();
        ev.stopPropagation();
        const ws = wsRef.current;
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(new TextEncoder().encode("\x1b[13;2u"));
        }
      }
    };
    container.addEventListener("keydown", handleShiftEnter, true);

    // Defer WebGL addon + initial fit to the next frame so the container
    // layout is fully settled and any prior WebGL contexts are cleaned up.
    const initRafId = requestAnimationFrame(() => {
      try {
        const webglAddon = new WebglAddon();
        webglAddon.onContextLoss(() => {
          webglAddon.dispose();
        });
        term.loadAddon(webglAddon);
      } catch {
        // WebGL not available, fall back to canvas renderer
      }
      fitAddon.fit();
    });

    // Defer WebSocket creation to the next microtask. This prevents React
    // StrictMode's mount→cleanup→remount cycle from creating two connections
    // to the same session — the first mount's timeout is cleared in cleanup
    // before it ever fires, so only one WebSocket (from the remount) connects.
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const params = initCommand
      ? `?init_command=${encodeURIComponent(initCommand)}`
      : "";
    const wsUrl = `${protocol}//${window.location.host}/ws/terminal/${sessionId}${params}`;

    const wsTimer = setTimeout(() => {
      const ws = new WebSocket(wsUrl);
      ws.binaryType = "arraybuffer";
      wsRef.current = ws;

      ws.onopen = () => {
        setSessionConnected(sessionId, true);
        // Fit to get definitive dimensions now that layout is settled
        fitAddon.fit();
        const dims = fitAddon.proposeDimensions();
        if (dims) {
          ws.send(
            JSON.stringify({ type: "resize", cols: dims.cols, rows: dims.rows }),
          );
        }
        // Expose send function for injection bar
        onSendReady?.((message: string) => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "inject", message }));
          }
        });
      };

      ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
          term.write(new Uint8Array(event.data));
        } else {
          term.write(event.data as string);
        }
      };

      ws.onclose = () => {
        setSessionConnected(sessionId, false);
      };

      // Forward terminal input to WS
      term.onData((data) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(new TextEncoder().encode(data));
        }
      });

      term.onBinary((data) => {
        if (ws.readyState === WebSocket.OPEN) {
          const buffer = new Uint8Array(data.length);
          for (let i = 0; i < data.length; i++) {
            buffer[i] = data.charCodeAt(i);
          }
          ws.send(buffer);
        }
      });
    }, 0);

    // ResizeObserver — skip when hidden (performance)
    const resizeObserver = new ResizeObserver(() => {
      if (!visibleRef.current) return;
      fitAddon.fit();
      const ws = wsRef.current;
      const dims = fitAddon.proposeDimensions();
      if (dims && ws?.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({ type: "resize", cols: dims.cols, rows: dims.rows }),
        );
      }
    });
    resizeObserver.observe(container);

    return () => {
      container.removeEventListener("keydown", handleShiftEnter, true);
      clearTimeout(wsTimer);
      cancelAnimationFrame(initRafId);
      resizeObserver.disconnect();
      const ws = wsRef.current;
      if (ws) ws.close();
      term.dispose();
      termRef.current = null;
      wsRef.current = null;
      fitAddonRef.current = null;
    };
  }, [sessionId, setSessionConnected]);

  // Re-fit when becoming visible
  useEffect(() => {
    if (visible && fitAddonRef.current) {
      requestAnimationFrame(() => {
        const fitAddon = fitAddonRef.current;
        const ws = wsRef.current;
        if (!fitAddon) return;
        fitAddon.fit();
        const dims = fitAddon.proposeDimensions();
        if (dims && ws?.readyState === WebSocket.OPEN) {
          ws.send(
            JSON.stringify({ type: "resize", cols: dims.cols, rows: dims.rows }),
          );
        }
      });
    }
  }, [visible]);

  return <div ref={containerRef} className="h-full w-full" />;
}
