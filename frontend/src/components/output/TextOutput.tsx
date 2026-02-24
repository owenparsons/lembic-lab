interface TextOutputProps {
  text: string;
  stream?: "stdout" | "stderr";
}

/**
 * Renders plain text / stream output with ANSI escape code stripping.
 * Full ANSI color support can be added later; for now we strip codes.
 */
export function TextOutput({ text, stream }: TextOutputProps) {
  const stripped = stripAnsi(text);

  return (
    <pre
      className={`whitespace-pre-wrap font-mono text-xs leading-5 ${
        stream === "stderr" ? "text-df-state-error" : "text-df-text-primary"
      }`}
    >
      {stripped}
    </pre>
  );
}

// Strip ANSI escape sequences for clean display
const ANSI_REGEX = /\x1b\[[0-9;]*[a-zA-Z]/g;

function stripAnsi(text: string): string {
  return text.replace(ANSI_REGEX, "");
}
