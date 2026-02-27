import { useCallback, useEffect, useState } from "react";
import { History, RefreshCw, RotateCcw } from "lucide-react";
import { get, post } from "../../services/api";

interface Checkpoint {
  hash: string;
  timestamp: string;
  message: string;
}

export function CheckpointPanel() {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [reverting, setReverting] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await get<Checkpoint[]>("/checkpoints");
      setCheckpoints(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleRevert = async (hash: string) => {
    if (!confirm(`Revert to checkpoint ${hash.slice(0, 8)}? This will restore all files to that point.`)) {
      return;
    }
    setReverting(hash);
    try {
      await post("/checkpoints/revert", { hash });
      // Reload page to pick up reverted files
      window.location.reload();
    } catch {
      alert("Revert failed.");
    } finally {
      setReverting(null);
    }
  };

  return (
    <div className="flex h-full flex-col bg-lb-bg-secondary">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-lb-border-primary px-3 py-2">
        <div className="flex items-center gap-2">
          <History size={14} className="text-lb-accent-primary" />
          <span className="text-xs font-semibold text-lb-text-primary">
            Checkpoints
          </span>
          <span className="text-xs text-lb-text-muted">
            ({checkpoints.length})
          </span>
        </div>
        <button
          onClick={() => refresh()}
          disabled={loading}
          className="rounded p-1 text-lb-text-muted transition-colors hover:bg-lb-bg-hover hover:text-lb-text-primary disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {/* Checkpoint list */}
      <div className="flex-1 overflow-y-auto">
        {checkpoints.length === 0 ? (
          <div className="px-3 py-4 text-center text-xs text-lb-text-muted">
            {loading ? "Loading..." : "No checkpoints yet"}
          </div>
        ) : (
          <div className="divide-y divide-lb-border-secondary">
            {checkpoints.map((cp) => (
              <div
                key={cp.hash}
                className="flex items-center gap-2 px-3 py-2 hover:bg-lb-bg-hover"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-lb-accent-primary">
                      {cp.hash.slice(0, 8)}
                    </span>
                    <span className="text-[10px] text-lb-text-muted">
                      {cp.timestamp}
                    </span>
                  </div>
                  <div className="truncate text-xs text-lb-text-secondary">
                    {cp.message}
                  </div>
                </div>
                <button
                  onClick={() => handleRevert(cp.hash)}
                  disabled={reverting !== null}
                  className="shrink-0 rounded p-1 text-lb-text-muted transition-colors hover:bg-lb-bg-tertiary hover:text-lb-text-primary disabled:opacity-50"
                  title="Revert to this checkpoint"
                >
                  <RotateCcw
                    size={13}
                    className={reverting === cp.hash ? "animate-spin" : ""}
                  />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
