import { ChevronDown, ChevronRight } from "lucide-react";
import type { NotebookSection } from "../../types/cell";

interface SectionDividerProps {
  section: NotebookSection;
  onToggle: () => void;
}

export function SectionDivider({ section, onToggle }: SectionDividerProps) {
  return (
    <button
      onClick={onToggle}
      className="flex w-full items-center gap-2 py-2 text-left"
    >
      {section.collapsed ? (
        <ChevronRight size={14} className="text-lb-text-muted" />
      ) : (
        <ChevronDown size={14} className="text-lb-text-muted" />
      )}
      <span className="text-xs font-semibold uppercase tracking-wider text-lb-text-secondary">
        {section.name}
      </span>
      <div className="h-px flex-1 bg-lb-border-secondary" />
    </button>
  );
}
