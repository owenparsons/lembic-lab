import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        df: {
          bg: {
            primary: "var(--df-bg-primary)",
            secondary: "var(--df-bg-secondary)",
            tertiary: "var(--df-bg-tertiary)",
            elevated: "var(--df-bg-elevated)",
            hover: "var(--df-bg-hover)",
            active: "var(--df-bg-active)",
          },
          text: {
            primary: "var(--df-text-primary)",
            secondary: "var(--df-text-secondary)",
            muted: "var(--df-text-muted)",
            disabled: "var(--df-text-disabled)",
          },
          border: {
            primary: "var(--df-border-primary)",
            secondary: "var(--df-border-secondary)",
            focus: "var(--df-border-focus)",
          },
          accent: {
            primary: "var(--df-accent-primary)",
            secondary: "var(--df-accent-secondary)",
          },
          state: {
            idle: "var(--df-state-idle)",
            running: "var(--df-state-running)",
            success: "var(--df-state-success)",
            error: "var(--df-state-error)",
            stale: "var(--df-state-stale)",
            "stale-upstream": "var(--df-state-stale-upstream)",
          },
        },
      },
      fontFamily: {
        mono: [
          "JetBrains Mono",
          "Fira Code",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
