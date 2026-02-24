import { useEffect } from "react";
import { AppShell } from "./components/layout/AppShell";
import { useNotebookStore } from "./stores/notebookStore";

function App() {
  const loadNotebook = useNotebookStore((s) => s.loadNotebook);

  useEffect(() => {
    loadNotebook();
  }, [loadNotebook]);

  return <AppShell />;
}

export default App;
