/**
 * Keyboard shortcut definitions.
 */

export interface Shortcut {
  key: string;
  mod?: boolean; // Cmd on Mac, Ctrl on others
  shift?: boolean;
  alt?: boolean;
  label: string;
}

export const SHORTCUTS = {
  // Global
  save: { key: "s", mod: true, label: "Save" },
  runCell: { key: "Enter", shift: true, label: "Run cell" },
  runCellAndAdvance: { key: "Enter", mod: true, label: "Run cell & advance" },

  // Command mode
  addCellBelow: { key: "b", label: "Add cell below" },
  addCellAbove: { key: "a", label: "Add cell above" },
  deleteCell: { key: "d", label: "Delete cell (press twice)" },
  moveUp: { key: "ArrowUp", label: "Select previous cell" },
  moveDown: { key: "ArrowDown", label: "Select next cell" },
  enterEdit: { key: "Enter", label: "Enter edit mode" },
  escape: { key: "Escape", label: "Exit edit mode / command mode" },

  // Utility
  interrupt: { key: "i", label: "Interrupt kernel (press twice)" },
  restart: { key: "0", label: "Restart kernel (press twice)" },
  sendToTerminal: { key: "Enter", mod: true, shift: true, label: "Send to CC" },
} as const satisfies Record<string, Shortcut>;
