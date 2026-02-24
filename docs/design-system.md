# Design System

DataFlow uses a dark-mode-first design system. All colors are defined as CSS custom properties in `frontend/src/styles/globals.css` and mapped to Tailwind CSS utility classes via `frontend/tailwind.config.ts`.

## Color Palette

### Background Layers

Colors are layered from deepest (app background) to most elevated (tooltips, dropdowns):

| Token | Hex | Usage |
|-------|-----|-------|
| `--df-bg-primary` | `#0d1117` | App background |
| `--df-bg-secondary` | `#161b22` | Card/cell background |
| `--df-bg-tertiary` | `#1c2333` | Editor background, nested surfaces |
| `--df-bg-elevated` | `#21283b` | Dropdowns, tooltips |
| `--df-bg-hover` | `#292e3e` | Hover states |
| `--df-bg-active` | `#2d3548` | Active/pressed states |

### Text Hierarchy

| Token | Hex | Usage |
|-------|-----|-------|
| `--df-text-primary` | `#e6edf3` | Body text |
| `--df-text-secondary` | `#9ca3b0` | Labels, descriptions |
| `--df-text-muted` | `#6b7280` | Timestamps, hints |
| `--df-text-disabled` | `#484f5a` | Disabled elements |

### Borders

| Token | Hex | Usage |
|-------|-----|-------|
| `--df-border-primary` | `#30363d` | Cell outlines, dividers |
| `--df-border-secondary` | `#21262d` | Subtle separators |
| `--df-border-focus` | `#58a6ff` | Focus rings |

### Accent Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--df-accent-primary` | `#58a6ff` | Links, focus, active tabs |
| `--df-accent-secondary` | `#3b82f6` | Button backgrounds |

### Cell Execution States

Each cell state has a distinct color for immediate visual feedback:

| Token | Hex | Color | State |
|-------|-----|-------|-------|
| `--df-state-idle` | `#6b7280` | Gray | Never run |
| `--df-state-running` | `#58a6ff` | Blue | Currently executing |
| `--df-state-success` | `#3fb950` | Green | Completed successfully |
| `--df-state-error` | `#f85149` | Red | Execution error |
| `--df-state-stale` | `#d29922` | Amber | Modified since last run |
| `--df-state-stale-upstream` | `#db6d28` | Orange | Upstream dependency changed |

### Syntax Highlighting

Monaco editor and code display use these colors:

| Token | Hex | Usage |
|-------|-----|-------|
| `--df-syntax-keyword` | `#ff7b72` | `if`, `def`, `return`, `import` |
| `--df-syntax-string` | `#a5d6ff` | String literals |
| `--df-syntax-comment` | `#8b949e` | Comments |
| `--df-syntax-function` | `#d2a8ff` | Function names |
| `--df-syntax-variable` | `#ffa657` | Variable names |
| `--df-syntax-number` | `#79c0ff` | Number literals |
| `--df-syntax-type` | `#7ee787` | Type annotations |

## Tailwind Integration

All CSS custom properties are mapped to Tailwind utility classes with the `df-` prefix:

```css
/* In globals.css */
:root {
  --df-bg-primary: #0d1117;
  /* ... */
}

/* In tailwind.config.ts */
colors: {
  df: {
    bg: {
      primary: "var(--df-bg-primary)",
      secondary: "var(--df-bg-secondary)",
      /* ... */
    },
    text: {
      primary: "var(--df-text-primary)",
      /* ... */
    }
  }
}
```

Usage in components:

```tsx
<div className="bg-df-bg-secondary text-df-text-primary border-df-border-primary">
  ...
</div>
```

## Monaco Editor Theme

The Monaco editor uses a custom theme (`dataflow-dark`) defined in `frontend/src/components/editor/monacoConfig.ts`. The theme matches the design system:

- Editor background: `#1c2333` (tertiary)
- Line numbers: `#6b7280` (muted)
- Selection: `#264f78`
- Syntax colors match the CSS variables above

## xterm.js Theme

The terminal uses a matching dark theme defined in `frontend/src/constants/theme.ts` via the `XTERM_THEME` object, ensuring visual consistency between the code editor and terminal.

## Layout

The main layout uses `react-resizable-panels` with:

- **Notebook pane** (default 60%): toolbar + scrollable cell list
- **Terminal pane** (default 40%): terminal header + xterm.js + injection bar
- **Side panels** (320-360px fixed width): variable explorer, data profiler, dependency graph

Panes can be swapped (terminal left, notebook right) via the PaneHandle swap button. Side panels open/close from the toolbar.
