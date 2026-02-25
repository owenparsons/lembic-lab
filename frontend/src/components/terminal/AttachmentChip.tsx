import { X } from "lucide-react";
import type { TerminalAttachment } from "../../types/terminal";

interface AttachmentChipProps {
  attachment: TerminalAttachment;
  onRemove: () => void;
}

export function AttachmentChip({ attachment, onRemove }: AttachmentChipProps) {
  return (
    <span className="inline-flex items-center gap-1 rounded bg-lb-bg-active px-2 py-0.5 text-xs text-lb-text-secondary">
      <span className="font-mono">{attachment.cell_name}</span>
      <button
        onClick={onRemove}
        className="rounded p-0.5 hover:bg-lb-bg-hover hover:text-lb-text-primary"
      >
        <X size={10} />
      </button>
    </span>
  );
}
