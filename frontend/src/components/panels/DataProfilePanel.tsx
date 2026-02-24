import { X, BarChart3 } from "lucide-react";
import { useProfileStore } from "../../stores/profileStore";
import { useUiStore } from "../../stores/uiStore";
import { ProfileCard } from "./ProfileCard";
import { formatBytes } from "../../utils/formatters";

export function DataProfilePanel() {
  const profiles = useProfileStore((s) => s.profiles);
  const loading = useProfileStore((s) => s.loading);
  const toggleProfilePanel = useUiStore((s) => s.toggleProfilePanel);

  const profileList = Object.values(profiles);

  return (
    <div className="flex h-full flex-col border-l border-df-border-primary bg-df-bg-secondary">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-df-border-primary px-3 py-2">
        <div className="flex items-center gap-2">
          <BarChart3 size={14} className="text-df-accent-primary" />
          <span className="text-xs font-semibold text-df-text-primary">
            Data Profiles
          </span>
        </div>
        <button
          onClick={toggleProfilePanel}
          className="rounded p-1 text-df-text-muted transition-colors hover:bg-df-bg-hover hover:text-df-text-primary"
          title="Close"
        >
          <X size={13} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {loading && (
          <div className="text-center text-xs text-df-text-muted">
            Profiling...
          </div>
        )}

        {profileList.length === 0 && !loading ? (
          <div className="text-center text-xs text-df-text-muted py-4">
            No profiles yet. Click a DataFrame variable in the Variable Explorer
            to profile it.
          </div>
        ) : (
          profileList.map((profile) => (
            <div key={profile.variable_name}>
              {/* Profile header */}
              <div className="mb-2 flex items-center justify-between">
                <span className="font-mono text-sm font-semibold text-df-text-primary">
                  {profile.variable_name}
                </span>
                <span className="text-xs text-df-text-muted">
                  {profile.shape[0]} rows × {profile.shape[1]} cols
                  {profile.memory_usage_bytes > 0 && (
                    <> · {formatBytes(profile.memory_usage_bytes)}</>
                  )}
                </span>
              </div>

              {/* Column profiles */}
              <div className="space-y-2">
                {profile.columns.map((col) => (
                  <ProfileCard key={col.name} column={col} totalRows={profile.shape[0]} />
                ))}
              </div>

              {/* Sample rows */}
              {profile.sample_rows.length > 0 && (
                <div className="mt-3">
                  <div className="mb-1 text-xs font-semibold text-df-text-secondary">
                    Sample Rows
                  </div>
                  <div className="max-h-[200px] overflow-auto rounded border border-df-border-secondary">
                    <table className="w-full border-collapse text-xs">
                      <thead className="sticky top-0">
                        <tr>
                          {Object.keys(profile.sample_rows[0]!).map((key) => (
                            <th
                              key={key}
                              className="border-b border-r border-df-border-secondary bg-df-bg-tertiary px-2 py-1 text-left font-semibold text-df-text-secondary"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {profile.sample_rows.map((row, i) => (
                          <tr key={i} className="even:bg-df-bg-secondary">
                            {Object.values(row).map((val, j) => (
                              <td
                                key={j}
                                className="border-r border-df-border-secondary px-2 py-1 text-df-text-primary"
                              >
                                {val == null ? "—" : String(val)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
