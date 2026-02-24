import { Panel, Group } from "react-resizable-panels";
import { useUiStore } from "../../stores/uiStore";
import { NotebookPane } from "./NotebookPane";
import { TerminalPane } from "./TerminalPane";
import { PaneHandle } from "./PaneHandle";
import { StatusBar } from "./StatusBar";
import { Toolbar } from "../toolbar/Toolbar";
import { CellList } from "../cells/CellList";

export function AppShell() {
  const paneOrder = useUiStore((s) => s.paneOrder);

  const notebookPanel = (
    <Panel key="notebook" defaultSize={60} minSize={20}>
      <NotebookPane>
        <Toolbar />
        <div className="flex-1 overflow-y-auto">
          <CellList />
        </div>
      </NotebookPane>
    </Panel>
  );

  const terminalPanel = (
    <Panel key="terminal" defaultSize={40} minSize={15}>
      <TerminalPane />
    </Panel>
  );

  const first = paneOrder === "notebook-terminal" ? notebookPanel : terminalPanel;
  const second = paneOrder === "notebook-terminal" ? terminalPanel : notebookPanel;

  return (
    <div className="flex h-screen flex-col bg-df-bg-primary">
      <Group orientation="horizontal" className="flex-1">
        {first}
        <PaneHandle />
        {second}
      </Group>
      <StatusBar />
    </div>
  );
}
