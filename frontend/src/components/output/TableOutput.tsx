import { useMemo } from "react";

interface TableOutputProps {
  data: Record<string, unknown>[];
  maxRows?: number;
}

/**
 * Renders tabular data (e.g. DataFrame.to_json output) as a styled table.
 * Shows row/column counts and truncates large datasets.
 */
export function TableOutput({ data, maxRows = 50 }: TableOutputProps) {
  const columns = useMemo(() => {
    if (data.length === 0) return [];
    return Object.keys(data[0]!);
  }, [data]);

  const visibleRows = data.slice(0, maxRows);
  const truncated = data.length > maxRows;

  if (columns.length === 0) {
    return (
      <div className="text-xs text-df-text-muted">Empty DataFrame</div>
    );
  }

  return (
    <div className="overflow-hidden rounded border border-df-border-secondary">
      <div className="flex items-center justify-between bg-df-bg-secondary px-3 py-1.5">
        <span className="text-xs text-df-text-muted">
          {data.length} rows × {columns.length} columns
        </span>
      </div>
      <div className="max-h-[400px] overflow-auto">
        <table className="w-full border-collapse text-xs">
          <thead className="sticky top-0 z-10">
            <tr>
              <th className="border-b border-r border-df-border-secondary bg-df-bg-tertiary px-2 py-1.5 text-left font-semibold text-df-text-secondary">
                #
              </th>
              {columns.map((col) => (
                <th
                  key={col}
                  className="border-b border-r border-df-border-secondary bg-df-bg-tertiary px-2 py-1.5 text-left font-semibold text-df-text-primary"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, i) => (
              <tr
                key={i}
                className="even:bg-df-bg-secondary hover:bg-df-bg-hover"
              >
                <td className="border-r border-df-border-secondary px-2 py-1 text-df-text-muted">
                  {i}
                </td>
                {columns.map((col) => (
                  <td
                    key={col}
                    className="border-r border-df-border-secondary px-2 py-1 text-df-text-primary"
                  >
                    {formatCellValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {truncated && (
        <div className="border-t border-df-border-secondary bg-df-bg-secondary px-3 py-1.5 text-xs text-df-text-muted">
          Showing {maxRows} of {data.length} rows
        </div>
      )}
    </div>
  );
}

function formatCellValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    if (Number.isInteger(value)) return String(value);
    return value.toFixed(4);
  }
  if (typeof value === "boolean") return value ? "true" : "false";
  const str = String(value);
  return str.length > 100 ? str.slice(0, 97) + "..." : str;
}
