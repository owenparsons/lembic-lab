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
    <div className="flex h-full flex-col border-l border-lb-border-primary bg-lb-bg-secondary">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-lb-border-primary px-3 py-2">
        <div className="flex items-center gap-2">
          <BarChart3 size={14} className="text-lb-accent-primary" />
          <span className="text-xs font-semibold text-lb-text-primary">
            Data Profiles
          </span>
        </div>
        <button
          onClick={toggleProfilePanel}
          className="rounded p-1 text-lb-text-muted transition-colors hover:bg-lb-bg-hover hover:text-lb-text-primary"
          title="Close"
        >
          <X size={13} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {loading && (
          <div className="text-center text-xs text-lb-text-muted">
            Profiling...
          </div>
        )}

        {profileList.length === 0 && !loading ? (
          <div className="text-center text-xs text-lb-text-muted py-4">
            No profiles yet. Click a DataFrame variable in the Variable Explorer
            to profile it.
          </div>
        ) : (
          profileList.map((profile) => (
            <div key={profile.variable_name}>
              {/* Profile header */}
              <div className="mb-2 flex items-center justify-between">
                <span className="font-mono text-sm font-semibold text-lb-text-primary">
                  {profile.variable_name}
                </span>
                <span className="text-xs text-lb-text-muted">
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
                  <div className="mb-1 text-xs font-semibold text-lb-text-secondary">
                    Sample Rows
                  </div>
                  <div className="max-h-[200px] overflow-auto rounded border border-lb-border-secondary">
                    <table className="w-full border-collapse text-xs">
                      <thead className="sticky top-0">
                        <tr>
                          {Object.keys(profile.sample_rows[0]!).map((key) => (
                            <th
                              key={key}
                              className="border-b border-r border-lb-border-secondary bg-lb-bg-tertiary px-2 py-1 text-left font-semibold text-lb-text-secondary"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {profile.sample_rows.map((row, i) => (
                          <tr key={i} className="even:bg-lb-bg-secondary">
                            {Object.values(row).map((val, j) => (
                              <td
                                key={j}
                                className="border-r border-lb-border-secondary px-2 py-1 text-lb-text-primary"
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
