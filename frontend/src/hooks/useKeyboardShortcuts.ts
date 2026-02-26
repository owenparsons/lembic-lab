import { useEffect, useRef, useCallback } from "react";
import { useNotebookStore } from "../stores/notebookStore";
import { useUiStore } from "../stores/uiStore";
import { executionApi } from "../services/executionApi";

/**
 * Global keyboard shortcut handler with command/edit mode awareness.
 * Modeled after Jupyter's dual-mode keyboard system.
 */
export function useKeyboardShortcuts() {
  const mode = useUiStore((s) => s.mode);
  const setMode = useUiStore((s) => s.setMode);
  const selectedCellId = useUiStore((s) => s.selectedCellId);
  const selectCell = useUiStore((s) => s.selectCell);
  const lastDeleteRef = useRef(0);
  const lastInterruptRef = useRef(0);
  const lastRestartRef = useRef(0);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      const target = e.target as HTMLElement;
      const isInputElement =
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable;

      // --- Global shortcuts (work in any mode) ---

      // Cmd+S: Save
      if (mod && e.key === "s") {
        e.preventDefault();
        useNotebookStore.getState().saveAll();
        return;
      }

      // Shift+Enter: Run cell and stay (works in both command and edit mode)
      // Skip when focus is in terminal, input fields, or Monaco (which has its own binding)
      const isTerminal = target.closest(".xterm") != null;
      if (e.shiftKey && e.key === "Enter" && !mod && !isInputElement && !isTerminal && selectedCellId) {
        e.preventDefault();
        if (selectedCellId) {
          const state = useNotebookStore.getState();
          if (state.dirty.has(selectedCellId)) {
            state.saveCell(selectedCellId).then(() => {
              executionApi.runCell(selectedCellId);
            });
          } else {
            executionApi.runCell(selectedCellId);
          }
        }
        return;
      }

      // Cmd+Enter: Run cell and advance
      if (mod && e.key === "Enter" && !e.shiftKey && mode === "command") {
        e.preventDefault();
        if (selectedCellId) {
          const store = useNotebookStore.getState();
          const cells = store.cells;
          const idx = cells.findIndex((c) => c.id === selectedCellId);

          const run = async () => {
            if (store.dirty.has(selectedCellId)) {
              await store.saveCell(selectedCellId);
            }
            await executionApi.runCell(selectedCellId);
            // Advance to next cell
            if (idx < cells.length - 1) {
              selectCell(cells[idx + 1]!.id);
            }
          };
          run();
        }
        return;
      }

      // --- Command mode shortcuts ---
      if (mode === "command" && !isInputElement) {
        switch (e.key) {
          case "Enter":
            e.preventDefault();
            setMode("edit");
            break;

          case "Escape":
            e.preventDefault();
            selectCell(null);
            break;

          case "ArrowUp":
          case "k": {
            e.preventDefault();
            const cells = useNotebookStore.getState().cells;
            if (!selectedCellId) {
              if (cells.length > 0) selectCell(cells[cells.length - 1]!.id);
            } else {
              const idx = cells.findIndex((c) => c.id === selectedCellId);
              if (idx > 0) selectCell(cells[idx - 1]!.id);
            }
            break;
          }

          case "ArrowDown":
          case "j": {
            e.preventDefault();
            const cells = useNotebookStore.getState().cells;
            if (!selectedCellId) {
              if (cells.length > 0) selectCell(cells[0]!.id);
            } else {
              const idx = cells.findIndex((c) => c.id === selectedCellId);
              if (idx < cells.length - 1) selectCell(cells[idx + 1]!.id);
            }
            break;
          }

          case "b": {
            // Add cell below
            e.preventDefault();
            const store = useNotebookStore.getState();
            store.addCell({ type: "code", after_id: selectedCellId ?? undefined }).then((cell) => {
              if (cell) {
                selectCell(cell.id);
                setMode("edit");
              }
            });
            break;
          }

          case "a": {
            // Add cell above
            e.preventDefault();
            const store = useNotebookStore.getState();
            const cells = store.cells;
            const idx = selectedCellId
              ? cells.findIndex((c) => c.id === selectedCellId)
              : 0;
            const afterId = idx > 0 ? cells[idx - 1]!.id : undefined;
            store.addCell({ type: "code", after_id: afterId }).then((cell) => {
              if (cell) {
                selectCell(cell.id);
                setMode("edit");
              }
            });
            break;
          }

          case "d": {
            // Delete cell (press twice within 500ms)
            const now = Date.now();
            if (now - lastDeleteRef.current < 500 && selectedCellId) {
              e.preventDefault();
              const store = useNotebookStore.getState();
              const cells = store.cells;
              const idx = cells.findIndex((c) => c.id === selectedCellId);
              store.deleteCell(selectedCellId);
              // Select adjacent cell
              if (idx > 0) selectCell(cells[idx - 1]!.id);
              else if (cells.length > 1) selectCell(cells[1]!.id);
              else selectCell(null);
              lastDeleteRef.current = 0;
            } else {
              lastDeleteRef.current = now;
            }
            break;
          }

          case "i": {
            // Interrupt kernel (press twice within 500ms)
            const now = Date.now();
            if (now - lastInterruptRef.current < 500) {
              e.preventDefault();
              executionApi.interrupt();
              lastInterruptRef.current = 0;
            } else {
              lastInterruptRef.current = now;
            }
            break;
          }

          case "0": {
            // Restart kernel (press twice within 500ms)
            const now = Date.now();
            if (now - lastRestartRef.current < 500) {
              e.preventDefault();
              executionApi.restart();
              lastRestartRef.current = 0;
            } else {
              lastRestartRef.current = now;
            }
            break;
          }

          case "m": {
            // Change cell type to markdown
            if (selectedCellId) {
              e.preventDefault();
              // Would need backend support for type change
            }
            break;
          }

          case "y": {
            // Change cell type to code
            if (selectedCellId) {
              e.preventDefault();
              // Would need backend support for type change
            }
            break;
          }
        }
      }

      // --- Edit mode: only Escape ---
      if (mode === "edit" && e.key === "Escape" && !isInputElement) {
        // Monaco handles its own Escape; this catches other cases
        e.preventDefault();
        setMode("command");
      }
    },
    [mode, setMode, selectedCellId, selectCell],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
}
