import type { CellOutput as CellOutputType } from "../../types/cell";
import { bestMimeType } from "../../utils/mimeType";

interface CellOutputProps {
  outputs: CellOutputType[];
}

export function CellOutput({ outputs }: CellOutputProps) {
  if (outputs.length === 0) return null;

  return (
    <div className="border-t border-df-border-secondary bg-df-bg-primary px-3 py-2">
      {outputs.map((output, i) => (
        <OutputItem key={i} output={output} />
      ))}
    </div>
  );
}

function OutputItem({ output }: { output: CellOutputType }) {
  switch (output.type) {
    case "stream":
      return (
        <pre
          className={`whitespace-pre-wrap font-mono text-xs ${
            output.stream === "stderr" ? "text-df-state-error" : "text-df-text-primary"
          }`}
        >
          {output.text}
        </pre>
      );

    case "execute_result":
    case "display_data": {
      const mime = bestMimeType(output.data);
      if (!mime) return null;

      if (mime === "image/png") {
        const src = `data:image/png;base64,${output.data["image/png"] as string}`;
        return <img src={src} alt="Output" className="max-w-full rounded" />;
      }

      if (mime === "image/svg+xml") {
        return (
          <div
            className="max-w-full"
            dangerouslySetInnerHTML={{ __html: output.data["image/svg+xml"] as string }}
          />
        );
      }

      if (mime === "text/html") {
        return (
          <div
            className="max-w-full overflow-auto text-xs text-df-text-primary"
            dangerouslySetInnerHTML={{ __html: output.data["text/html"] as string }}
          />
        );
      }

      if (mime === "text/plain") {
        return (
          <pre className="whitespace-pre-wrap font-mono text-xs text-df-text-primary">
            {output.data["text/plain"] as string}
          </pre>
        );
      }

      return (
        <pre className="whitespace-pre-wrap font-mono text-xs text-df-text-muted">
          [{mime}]
        </pre>
      );
    }

    case "error":
      return (
        <div className="rounded bg-df-state-error/10 p-2">
          <pre className="whitespace-pre-wrap font-mono text-xs text-df-state-error">
            {output.ename}: {output.evalue}
          </pre>
          {output.traceback.length > 0 && (
            <pre className="mt-1 whitespace-pre-wrap font-mono text-xs text-df-text-secondary">
              {output.traceback.join("\n")}
            </pre>
          )}
        </div>
      );

    default:
      return null;
  }
}
