/**
 * Determine the best MIME type to render from display_data.
 */

const PRIORITY = [
  "text/html",
  "image/svg+xml",
  "image/png",
  "image/jpeg",
  "application/json",
  "text/plain",
];

export function bestMimeType(data: Record<string, unknown>): string | null {
  for (const mime of PRIORITY) {
    if (mime in data) return mime;
  }
  // Fallback to first available
  const keys = Object.keys(data);
  return keys.length > 0 ? keys[0]! : null;
}
