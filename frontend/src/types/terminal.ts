export interface TerminalResizeMessage {
  type: "resize";
  cols: number;
  rows: number;
}

export interface TerminalInjectMessage {
  type: "inject";
  message: string;
  attachments: TerminalAttachment[];
}

export interface TerminalAttachment {
  cell_id: string;
  cell_name: string;
  content: string;
}
