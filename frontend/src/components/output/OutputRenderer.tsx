import type { CellOutput } from "../../types/cell";
import { bestMimeType } from "../../utils/mimeType";
import { TextOutput } from "./TextOutput";
import { ImageOutput } from "./ImageOutput";
import { HtmlOutput } from "./HtmlOutput";
import { TableOutput } from "./TableOutput";
import { ErrorOutput } from "./ErrorOutput";

interface OutputRendererProps {
  outputs: CellOutput[];
}

/**
 * Main output dispatcher: renders a list of cell outputs using
 * the appropriate specialized component for each output type.
 */
export function OutputRenderer({ outputs }: OutputRendererProps) {
  if (outputs.length === 0) return null;

  return (
    <div className="border-t border-lb-border-secondary bg-lb-bg-primary px-3 py-2 space-y-2">
      {outputs.map((output, i) => (
        <OutputItem key={i} output={output} />
      ))}
    </div>
  );
}

function OutputItem({ output }: { output: CellOutput }) {
  switch (output.type) {
    case "stream":
      return <TextOutput text={output.text} stream={output.stream} />;

    case "execute_result":
    case "display_data":
      return <RichOutput data={output.data} />;

    case "error":
      return (
        <ErrorOutput
          ename={output.ename}
          evalue={output.evalue}
          traceback={output.traceback}
        />
      );

    default:
      return null;
  }
}

function RichOutput({ data }: { data: Record<string, unknown> }) {
  const mime = bestMimeType(data);
  if (!mime) return null;

  // Image types
  if (mime.startsWith("image/")) {
    return <ImageOutput data={data} />;
  }

  // HTML (Plotly, Altair, DataFrame HTML repr)
  if (mime === "text/html") {
    return <HtmlOutput html={data["text/html"] as string} />;
  }

  // JSON (typically DataFrame.to_json)
  if (mime === "application/json") {
    const jsonData = data["application/json"];
    if (Array.isArray(jsonData)) {
      return <TableOutput data={jsonData as Record<string, unknown>[]} />;
    }
    return (
      <pre className="whitespace-pre-wrap font-mono text-xs text-lb-text-primary">
        {JSON.stringify(jsonData, null, 2)}
      </pre>
    );
  }

  // Plain text fallback
  if (mime === "text/plain") {
    return <TextOutput text={data["text/plain"] as string} />;
  }

  // Unknown mime type
  return (
    <pre className="font-mono text-xs text-lb-text-muted">[{mime}]</pre>
  );
}
