/**
 * Design tokens as JS values for programmatic use (xterm, Monaco themes).
 * CSS custom properties are the source of truth in globals.css.
 */

export const THEME = {
  bg: {
    primary: "#0d1117",
    secondary: "#161b22",
    tertiary: "#1c2333",
    elevated: "#21283b",
    hover: "#292e3e",
    active: "#2d3548",
  },
  text: {
    primary: "#e6edf3",
    secondary: "#9ca3b0",
    muted: "#6b7280",
    disabled: "#484f5a",
  },
  border: {
    primary: "#30363d",
    secondary: "#21262d",
    focus: "#58a6ff",
  },
  accent: {
    primary: "#58a6ff",
    secondary: "#3b82f6",
  },
  state: {
    idle: "#6b7280",
    running: "#58a6ff",
    success: "#3fb950",
    error: "#f85149",
    stale: "#d29922",
    staleUpstream: "#db6d28",
  },
  syntax: {
    keyword: "#ff7b72",
    string: "#a5d6ff",
    comment: "#8b949e",
    function: "#d2a8ff",
    variable: "#ffa657",
    number: "#79c0ff",
    type: "#7ee787",
  },
} as const;

/** xterm.js ITheme config */
export const XTERM_THEME = {
  background: THEME.bg.primary,
  foreground: THEME.text.primary,
  cursor: THEME.accent.primary,
  cursorAccent: THEME.bg.primary,
  selectionBackground: "rgba(88, 166, 255, 0.3)",
  black: "#484f58",
  red: "#ff7b72",
  green: "#3fb950",
  yellow: "#d29922",
  blue: "#58a6ff",
  magenta: "#d2a8ff",
  cyan: "#39d353",
  white: "#e6edf3",
  brightBlack: "#6e7681",
  brightRed: "#ffa198",
  brightGreen: "#56d364",
  brightYellow: "#e3b341",
  brightBlue: "#79c0ff",
  brightMagenta: "#d2a8ff",
  brightCyan: "#56d364",
  brightWhite: "#f0f6fc",
};
