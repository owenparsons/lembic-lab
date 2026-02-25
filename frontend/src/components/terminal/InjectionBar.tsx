import { Send } from "lucide-react";
import { useTerminalStore } from "../../stores/terminalStore";
import { AttachmentChip } from "./AttachmentChip";
import { IconButton } from "../shared/IconButton";

interface InjectionBarProps {
  onSend: (message: string) => void;
}

export function InjectionBar({ onSend }: InjectionBarProps) {
  const { attachments, injectionMessage, setInjectionMessage, removeAttachment, clearInjection } =
    useTerminalStore();

  const handleSend = () => {
    if (!injectionMessage.trim() && attachments.length === 0) return;

    // Build composite message with attachments
    let message = "";
    if (attachments.length > 0) {
      for (const att of attachments) {
        message += `<cell name="${att.cell_name}" id="${att.cell_id}">\n${att.content}\n</cell>\n\n`;
      }
    }
    message += injectionMessage;

    onSend(message + "\n");
    clearInjection();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-lb-border-secondary bg-lb-bg-secondary p-2">
      {attachments.length > 0 && (
        <div className="mb-1.5 flex flex-wrap gap-1">
          {attachments.map((att) => (
            <AttachmentChip
              key={att.cell_id}
              attachment={att}
              onRemove={() => removeAttachment(att.cell_id)}
            />
          ))}
        </div>
      )}
      <div className="flex items-end gap-1.5">
        <textarea
          value={injectionMessage}
          onChange={(e) => setInjectionMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message to CC..."
          rows={1}
          className="flex-1 resize-none rounded border border-lb-border-primary bg-lb-bg-tertiary px-2 py-1.5 text-xs text-lb-text-primary placeholder:text-lb-text-muted focus:border-lb-border-focus focus:outline-none"
        />
        <IconButton icon={Send} label="Send" onClick={handleSend} />
      </div>
    </div>
  );
}
