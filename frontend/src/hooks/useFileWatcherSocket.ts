import { useCallback } from "react";
import { useWebSocket } from "./useWebSocket";
import { useNotebookStore } from "../stores/notebookStore";
import type { FileWatcherMessage } from "../types/ws";

export function useFileWatcherSocket() {
  const updateContent = useNotebookStore((s) => s.updateContent);
  const loadNotebook = useNotebookStore((s) => s.loadNotebook);
  const dirty = useNotebookStore((s) => s.dirty);

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      let msg: FileWatcherMessage;
      try {
        msg = JSON.parse(event.data as string) as FileWatcherMessage;
      } catch {
        return;
      }

      switch (msg.type) {
        case "cell_modified": {
          // Only update if cell is not dirty (user isn't editing it)
          if (!dirty.has(msg.cell_id)) {
            updateContent(msg.cell_id, msg.new_content);
          }
          break;
        }

        case "manifest_modified": {
          // Reload the full notebook
          loadNotebook();
          break;
        }

        case "output_added":
          // Could trigger output refresh
          break;
      }
    },
    [updateContent, loadNotebook, dirty],
  );

  const { connected } = useWebSocket({
    url: "/ws/filewatcher",
    onMessage: handleMessage,
  });

  return { connected };
}
