import { useEffect } from "react";
import { AppShell } from "./components/layout/AppShell";
import { useNotebookStore } from "./stores/notebookStore";
import { useKernelSocket } from "./hooks/useKernelSocket";

function App() {
  const loadNotebook = useNotebookStore((s) => s.loadNotebook);

  // Connect kernel WebSocket
  useKernelSocket();

  useEffect(() => {
    loadNotebook();
  }, [loadNotebook]);

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + S → Save all
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        useNotebookStore.getState().saveAll();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return <AppShell />;
}

export default App;
