import { useState, useRef } from "react";
import { Loader2 } from "lucide-react";
import { useEnvironmentStore } from "../../stores/environmentStore";

export function PackageInstall() {
  const [value, setValue] = useState("");
  const [flash, setFlash] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const installing = useEnvironmentStore((s) => s.installing);
  const install = useEnvironmentStore((s) => s.install);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async () => {
    const packages = value
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean);
    if (packages.length === 0) return;

    try {
      const result = await install(packages);
      if (result.success) {
        setValue("");
        setFlash({ type: "success", text: `Installed ${packages.join(", ")}` });
      } else {
        setFlash({ type: "error", text: "Install failed" });
      }
    } catch {
      setFlash({ type: "error", text: "Install failed" });
    }

    setTimeout(() => setFlash(null), 3000);
  };

  return (
    <div className="flex items-center gap-1.5">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !installing) handleSubmit();
          }}
          placeholder="Install package..."
          disabled={installing}
          className="h-6 w-36 rounded border border-lb-border-secondary bg-lb-bg-primary px-2 text-xs text-lb-text-primary placeholder:text-lb-text-muted focus:border-lb-accent-primary focus:outline-none disabled:opacity-50"
        />
        {installing && (
          <Loader2
            size={12}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 animate-spin text-lb-text-muted"
          />
        )}
      </div>
      {flash && (
        <span
          className={`text-xs ${flash.type === "success" ? "text-lb-state-success" : "text-lb-state-error"}`}
        >
          {flash.text}
        </span>
      )}
    </div>
  );
}
