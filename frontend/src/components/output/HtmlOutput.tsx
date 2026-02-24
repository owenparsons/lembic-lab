import { useRef, useEffect, useState } from "react";

interface HtmlOutputProps {
  html: string;
}

/**
 * Renders HTML output in a sandboxed iframe.
 * Used for Plotly, Altair, and other interactive HTML outputs.
 * Auto-sizes the iframe to fit content.
 */
export function HtmlOutput({ html }: HtmlOutputProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(200);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const doc = iframe.contentDocument;
    if (!doc) return;

    // Inject dark-themed styles and content
    doc.open();
    doc.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body {
            margin: 0;
            padding: 8px;
            background: #0d1117;
            color: #e6edf3;
            font-family: system-ui, sans-serif;
            font-size: 13px;
          }
          table {
            border-collapse: collapse;
            width: 100%;
          }
          th, td {
            border: 1px solid #30363d;
            padding: 4px 8px;
            text-align: left;
          }
          th {
            background: #161b22;
            font-weight: 600;
          }
          tr:nth-child(even) {
            background: #161b22;
          }
        </style>
      </head>
      <body>${html}</body>
      </html>
    `);
    doc.close();

    // Auto-size after content loads
    const resize = () => {
      if (doc.body) {
        const newHeight = Math.min(doc.body.scrollHeight + 16, 600);
        setHeight(newHeight);
      }
    };

    // Try immediately and after a short delay (for async renders like Plotly)
    resize();
    const timer = setTimeout(resize, 500);
    return () => clearTimeout(timer);
  }, [html]);

  return (
    <iframe
      ref={iframeRef}
      className="w-full rounded border border-df-border-secondary"
      style={{ height: `${height}px` }}
      sandbox="allow-scripts allow-same-origin"
      title="HTML output"
    />
  );
}
