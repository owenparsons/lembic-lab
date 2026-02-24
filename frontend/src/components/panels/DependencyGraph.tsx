import { useMemo } from "react";
import { X, GitBranch } from "lucide-react";
import { useNotebookStore } from "../../stores/notebookStore";
import { useExecutionStore } from "../../stores/executionStore";
import { useUiStore } from "../../stores/uiStore";
import { CELL_STATE_CONFIG } from "../../constants/cellStates";
import type { CellState } from "../../types/cell";

interface DagNode {
  id: string;
  name: string;
  state: CellState;
  x: number;
  y: number;
  varsRead: string[];
  varsDefined: string[];
}

interface DagEdge {
  from: string;
  to: string;
  variable: string;
}

const NODE_WIDTH = 120;
const NODE_HEIGHT = 36;
const H_GAP = 40;
const V_GAP = 60;

export function DependencyGraph() {
  const cells = useNotebookStore((s) => s.cells);
  const cellStates = useExecutionStore((s) => s.cellStates);
  const logEntries = useExecutionStore((s) => s.logEntries);
  const toggleDependencyGraph = useUiStore((s) => s.toggleDependencyGraph);
  const selectCell = useUiStore((s) => s.selectCell);

  // Build dependency data from execution log
  const { nodes, edges } = useMemo(() => {
    // Build variable producer map from log entries
    const varProducer: Record<string, string> = {};
    const cellVarsRead: Record<string, string[]> = {};
    const cellVarsDefined: Record<string, string[]> = {};

    for (const entry of logEntries) {
      for (const v of entry.variables_defined) {
        varProducer[v] = entry.cell_id;
      }
      cellVarsRead[entry.cell_id] = entry.variables_read;
      cellVarsDefined[entry.cell_id] = entry.variables_defined;
    }

    // Build edges
    const edgeList: DagEdge[] = [];
    const inDegree: Record<string, number> = {};

    for (const cell of cells) {
      inDegree[cell.id] = 0;
    }

    for (const cell of cells) {
      const reads = cellVarsRead[cell.id] || [];
      for (const v of reads) {
        const producerId = varProducer[v];
        if (producerId && producerId !== cell.id) {
          edgeList.push({ from: producerId, to: cell.id, variable: v });
          inDegree[cell.id] = (inDegree[cell.id] || 0) + 1;
        }
      }
    }

    // Simple layered layout (topological order by notebook position)
    const nodeList: DagNode[] = [];
    const layer: Record<string, number> = {};

    // Assign layers based on dependencies
    const processed = new Set<string>();
    const queue = cells
      .filter((c) => (inDegree[c.id] || 0) === 0)
      .map((c) => c.id);

    for (const id of queue) {
      layer[id] = 0;
      processed.add(id);
    }

    let iterations = 0;
    while (queue.length > 0 && iterations < cells.length * 2) {
      const current = queue.shift()!;
      iterations++;
      for (const edge of edgeList) {
        if (edge.from === current && !processed.has(edge.to)) {
          layer[edge.to] = Math.max(layer[edge.to] || 0, (layer[current] || 0) + 1);
          // Check if all deps processed
          const allDepsProcessed = edgeList
            .filter((e) => e.to === edge.to)
            .every((e) => processed.has(e.from));
          if (allDepsProcessed) {
            processed.add(edge.to);
            queue.push(edge.to);
          }
        }
      }
    }

    // Assign unprocessed cells
    for (const cell of cells) {
      if (!(cell.id in layer)) {
        layer[cell.id] = 0;
      }
    }

    // Group by layer
    const layerGroups: Record<number, string[]> = {};
    for (const cell of cells) {
      const l = layer[cell.id] || 0;
      if (!layerGroups[l]) layerGroups[l] = [];
      layerGroups[l].push(cell.id);
    }

    // Position nodes
    const cellMap = Object.fromEntries(cells.map((c) => [c.id, c]));
    for (const [l, ids] of Object.entries(layerGroups)) {
      const layerNum = Number(l);
      ids.forEach((id, i) => {
        const cell = cellMap[id];
        if (cell) {
          nodeList.push({
            id: cell.id,
            name: cell.name,
            state: cellStates[cell.id] || "idle",
            x: layerNum * (NODE_WIDTH + H_GAP) + 20,
            y: i * (NODE_HEIGHT + V_GAP) + 20,
            varsRead: cellVarsRead[cell.id] || [],
            varsDefined: cellVarsDefined[cell.id] || [],
          });
        }
      });
    }

    return { nodes: nodeList, edges: edgeList };
  }, [cells, cellStates, logEntries]);

  const nodeMap = useMemo(
    () => Object.fromEntries(nodes.map((n) => [n.id, n])),
    [nodes],
  );

  const svgWidth = Math.max(
    ...nodes.map((n) => n.x + NODE_WIDTH + 20),
    300,
  );
  const svgHeight = Math.max(
    ...nodes.map((n) => n.y + NODE_HEIGHT + 20),
    200,
  );

  return (
    <div className="flex h-full flex-col border-l border-df-border-primary bg-df-bg-secondary">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-df-border-primary px-3 py-2">
        <div className="flex items-center gap-2">
          <GitBranch size={14} className="text-df-accent-primary" />
          <span className="text-xs font-semibold text-df-text-primary">
            Dependencies
          </span>
        </div>
        <button
          onClick={toggleDependencyGraph}
          className="rounded p-1 text-df-text-muted transition-colors hover:bg-df-bg-hover hover:text-df-text-primary"
          title="Close"
        >
          <X size={13} />
        </button>
      </div>

      {/* Graph */}
      <div className="flex-1 overflow-auto p-2">
        {nodes.length === 0 ? (
          <div className="py-4 text-center text-xs text-df-text-muted">
            Run cells to see dependency graph
          </div>
        ) : (
          <svg width={svgWidth} height={svgHeight} className="min-w-full">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="8"
                markerHeight="6"
                refX="8"
                refY="3"
                orient="auto"
              >
                <polygon
                  points="0 0, 8 3, 0 6"
                  fill="#6b7280"
                />
              </marker>
            </defs>

            {/* Edges */}
            {edges.map((edge, i) => {
              const from = nodeMap[edge.from];
              const to = nodeMap[edge.to];
              if (!from || !to) return null;

              const x1 = from.x + NODE_WIDTH;
              const y1 = from.y + NODE_HEIGHT / 2;
              const x2 = to.x;
              const y2 = to.y + NODE_HEIGHT / 2;
              const midX = (x1 + x2) / 2;

              return (
                <g key={i}>
                  <path
                    d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
                    fill="none"
                    stroke="#6b7280"
                    strokeWidth="1.5"
                    markerEnd="url(#arrowhead)"
                    opacity="0.6"
                  />
                  <text
                    x={midX}
                    y={(y1 + y2) / 2 - 4}
                    textAnchor="middle"
                    className="text-[9px] fill-df-text-muted"
                  >
                    {edge.variable}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {nodes.map((node) => {
              const config = CELL_STATE_CONFIG[node.state];
              return (
                <g
                  key={node.id}
                  className="cursor-pointer"
                  onClick={() => selectCell(node.id)}
                >
                  <rect
                    x={node.x}
                    y={node.y}
                    width={NODE_WIDTH}
                    height={NODE_HEIGHT}
                    rx="6"
                    className="fill-df-bg-tertiary stroke-df-border-primary"
                    strokeWidth="1"
                  />
                  {/* State indicator */}
                  <circle
                    cx={node.x + 12}
                    cy={node.y + NODE_HEIGHT / 2}
                    r="4"
                    fill={config?.color || "#6b7280"}
                  />
                  <text
                    x={node.x + 22}
                    y={node.y + NODE_HEIGHT / 2 + 4}
                    className="text-[10px] fill-df-text-primary"
                  >
                    {node.name.length > 12
                      ? node.name.slice(0, 10) + "..."
                      : node.name}
                  </text>
                </g>
              );
            })}
          </svg>
        )}
      </div>
    </div>
  );
}
