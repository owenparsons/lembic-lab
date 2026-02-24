import { useCallback } from "react";
import { useWebSocket } from "./useWebSocket";
import { useNotebookStore } from "../stores/notebookStore";
import { useKernelStore } from "../stores/kernelStore";
import { useExecutionStore } from "../stores/executionStore";
import type { KernelWsMessage } from "../types/ws";
import type { CellState, CellOutput } from "../types/cell";

export function useKernelSocket() {
  const setCellState = useNotebookStore((s) => s.setCellState);
  const appendOutput = useNotebookStore((s) => s.appendOutput);
  const clearOutputs = useNotebookStore((s) => s.clearOutputs);
  const setKernelStatus = useKernelStore((s) => s.setStatus);
  const { setCellState: setExecCellState, setRunning, setWarnings, setCellStates } = useExecutionStore();

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      let msg: KernelWsMessage;
      try {
        msg = JSON.parse(event.data as string) as KernelWsMessage;
      } catch {
        return;
      }

      switch (msg.type) {
        case "cell_status": {
          const state = msg.state as CellState;
          setCellState(msg.cell_id, state);
          setExecCellState(msg.cell_id, state);
          if (state === "running") {
            clearOutputs(msg.cell_id);
            setRunning(msg.cell_id);
          }
          break;
        }

        case "stream":
          appendOutput(msg.cell_id, msg as CellOutput);
          break;

        case "display_data":
          appendOutput(msg.cell_id, msg as CellOutput);
          break;

        case "execute_result":
          appendOutput(msg.cell_id, msg as CellOutput);
          break;

        case "error":
          appendOutput(msg.cell_id, msg as CellOutput);
          setCellState(msg.cell_id, "error");
          setExecCellState(msg.cell_id, "error");
          break;

        case "execute_reply": {
          const finalState: CellState = msg.status === "ok" ? "success" : "error";
          setCellState(msg.cell_id, finalState);
          setExecCellState(msg.cell_id, finalState);
          setRunning(null);
          break;
        }

        case "kernel_status":
          if (msg.status === "idle") setKernelStatus("idle");
          else if (msg.status === "busy") setKernelStatus("busy");
          break;

        case "cell_states":
          setCellStates(msg.states as Record<string, CellState>);
          setWarnings(msg.warnings);
          break;

        case "variables_update":
          // Handled by variable store refresh
          break;
      }
    },
    [setCellState, appendOutput, clearOutputs, setKernelStatus, setExecCellState, setRunning, setWarnings, setCellStates],
  );

  const { connected } = useWebSocket({
    url: "/ws/kernel",
    onMessage: handleMessage,
    onOpen: () => setKernelStatus("idle"),
    onClose: () => setKernelStatus("disconnected"),
  });

  return { connected };
}
