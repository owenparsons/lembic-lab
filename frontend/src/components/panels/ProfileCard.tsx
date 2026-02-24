import type { ColumnProfile } from "../../types/profile";

interface ProfileCardProps {
  column: ColumnProfile;
  totalRows: number;
}

export function ProfileCard({ column, totalRows }: ProfileCardProps) {
  const nullPct = totalRows > 0 ? (column.null_count / totalRows) * 100 : 0;
  const uniquePct = totalRows > 0 ? (column.unique_count / totalRows) * 100 : 0;
  const isNumeric = column.mean !== undefined;

  return (
    <div className="rounded border border-df-border-secondary bg-df-bg-primary p-2.5">
      {/* Column name and dtype */}
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-xs font-semibold text-df-text-primary">
          {column.name}
        </span>
        <span className="rounded bg-df-bg-tertiary px-1.5 py-0.5 text-[10px] font-mono text-df-text-muted">
          {column.dtype}
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-2 text-xs">
        <StatItem label="Count" value={column.count.toLocaleString()} />
        <StatItem
          label="Nulls"
          value={`${column.null_count} (${nullPct.toFixed(1)}%)`}
          alert={nullPct > 10}
        />
        <StatItem
          label="Unique"
          value={`${column.unique_count} (${uniquePct.toFixed(1)}%)`}
        />

        {isNumeric && (
          <>
            <StatItem label="Mean" value={formatNum(column.mean)} />
            <StatItem label="Std" value={formatNum(column.std)} />
            <StatItem label="Median" value={formatNum(column.median)} />
            <StatItem label="Min" value={formatNum(column.min as number | undefined)} />
            <StatItem label="Max" value={formatNum(column.max as number | undefined)} />
          </>
        )}
      </div>

      {/* Top values */}
      {column.top_values && column.top_values.length > 0 && (
        <div className="mt-2 border-t border-df-border-secondary pt-2">
          <div className="mb-1 text-[10px] font-semibold uppercase text-df-text-muted">
            Top Values
          </div>
          <div className="space-y-0.5">
            {column.top_values.map((tv, i) => {
              const val = String(tv.value ?? "");
              const count = Number(tv.count ?? 0);
              const pct = totalRows > 0 ? (count / totalRows) * 100 : 0;
              return (
                <div key={i} className="flex items-center gap-2">
                  <div
                    className="h-1.5 rounded-full bg-df-accent-primary/60"
                    style={{ width: `${Math.max(pct, 2)}%` }}
                  />
                  <span className="truncate font-mono text-[10px] text-df-text-primary">
                    {val}
                  </span>
                  <span className="ml-auto whitespace-nowrap text-[10px] text-df-text-muted">
                    {count} ({pct.toFixed(1)}%)
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function StatItem({
  label,
  value,
  alert,
}: {
  label: string;
  value: string;
  alert?: boolean;
}) {
  return (
    <div>
      <div className="text-[10px] text-df-text-muted">{label}</div>
      <div
        className={`font-mono text-xs ${
          alert ? "text-df-state-stale" : "text-df-text-primary"
        }`}
      >
        {value}
      </div>
    </div>
  );
}

function formatNum(val: number | undefined): string {
  if (val === undefined || val === null) return "—";
  if (Number.isInteger(val)) return val.toLocaleString();
  if (Math.abs(val) < 0.01 || Math.abs(val) > 99999) return val.toExponential(2);
  return val.toFixed(2);
}
