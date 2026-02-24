import { useEffect } from "react";
import { AppShell } from "./components/layout/AppShell";
import { useNotebookStore } from "./stores/notebookStore";
import { useKernelSocket } from "./hooks/useKernelSocket";
import { useFileWatcherSocket } from "./hooks/useFileWatcherSocket";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";

function App() {
  const loadNotebook = useNotebookStore((s) => s.loadNotebook);

  // Connect WebSockets
  useKernelSocket();
  useFileWatcherSocket();

  // Global keyboard shortcuts (command/edit mode aware)
  useKeyboardShortcuts();

  useEffect(() => {
    loadNotebook();
  }, [loadNotebook]);

  return <AppShell />;
}

export default App;
