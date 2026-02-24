import { useRef, useCallback } from "react";
import Editor, { type OnMount, type BeforeMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { DATAFLOW_DARK_THEME, EDITOR_OPTIONS } from "./monacoConfig";

interface MonacoWrapperProps {
  value: string;
  onChange: (value: string) => void;
  onRun?: () => void;
  onRunAndAdvance?: () => void;
  onEscape?: () => void;
  language?: string;
  readOnly?: boolean;
  minHeight?: number;
}

export function MonacoWrapper({
  value,
  onChange,
  onRun,
  onRunAndAdvance,
  onEscape,
  language = "python",
  readOnly = false,
  minHeight = 40,
}: MonacoWrapperProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleBeforeMount: BeforeMount = useCallback((monaco) => {
    monaco.editor.defineTheme("dataflow-dark", DATAFLOW_DARK_THEME);
  }, []);

  const handleMount: OnMount = useCallback(
    (editor, monaco) => {
      editorRef.current = editor;

      // Auto-height: resize editor to fit content
      const updateHeight = () => {
        const contentHeight = Math.max(
          editor.getContentHeight(),
          minHeight,
        );
        const maxHeight = 600;
        const height = Math.min(contentHeight, maxHeight);
        if (containerRef.current) {
          containerRef.current.style.height = `${height}px`;
        }
        editor.layout();
      };

      editor.onDidContentSizeChange(updateHeight);
      updateHeight();

      // Keybindings
      if (onRun) {
        editor.addAction({
          id: "dataflow-run-cell",
          label: "Run Cell",
          keybindings: [monaco.KeyMod.Shift | monaco.KeyCode.Enter],
          run: () => onRun(),
        });
      }

      if (onRunAndAdvance) {
        editor.addAction({
          id: "dataflow-run-and-advance",
          label: "Run Cell and Advance",
          keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
          run: () => onRunAndAdvance(),
        });
      }

      if (onEscape) {
        editor.addAction({
          id: "dataflow-escape",
          label: "Exit Edit Mode",
          keybindings: [monaco.KeyCode.Escape],
          run: () => onEscape(),
        });
      }
    },
    [onRun, onRunAndAdvance, onEscape, minHeight],
  );

  return (
    <div ref={containerRef} className="min-h-[40px] overflow-hidden rounded-b-md">
      <Editor
        value={value}
        onChange={(v) => onChange(v ?? "")}
        language={language}
        theme="dataflow-dark"
        options={{
          ...EDITOR_OPTIONS,
          readOnly,
        }}
        beforeMount={handleBeforeMount}
        onMount={handleMount}
      />
    </div>
  );
}
