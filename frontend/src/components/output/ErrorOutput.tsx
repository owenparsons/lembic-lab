interface ErrorOutputProps {
  ename: string;
  evalue: string;
  traceback: string[];
}

/**
 * Renders kernel error output with highlighted traceback.
 * Strips ANSI codes from traceback lines.
 */
export function ErrorOutput({ ename, evalue, traceback }: ErrorOutputProps) {
  const strippedTraceback = traceback.map(stripAnsi);

  return (
    <div className="rounded bg-df-state-error/10 p-3">
      <div className="font-mono text-xs font-semibold text-df-state-error">
        {ename}: {evalue}
      </div>
      {strippedTraceback.length > 0 && (
        <pre className="mt-2 whitespace-pre-wrap font-mono text-xs leading-5 text-df-text-secondary">
          {strippedTraceback.join("\n")}
        </pre>
      )}
    </div>
  );
}

const ANSI_REGEX = /\x1b\[[0-9;]*[a-zA-Z]/g;

function stripAnsi(text: string): string {
  return text.replace(ANSI_REGEX, "");
}
