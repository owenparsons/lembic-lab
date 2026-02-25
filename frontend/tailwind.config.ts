import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        lb: {
          bg: {
            primary: "var(--lb-bg-primary)",
            secondary: "var(--lb-bg-secondary)",
            tertiary: "var(--lb-bg-tertiary)",
            elevated: "var(--lb-bg-elevated)",
            hover: "var(--lb-bg-hover)",
            active: "var(--lb-bg-active)",
          },
          text: {
            primary: "var(--lb-text-primary)",
            secondary: "var(--lb-text-secondary)",
            muted: "var(--lb-text-muted)",
            disabled: "var(--lb-text-disabled)",
          },
          border: {
            primary: "var(--lb-border-primary)",
            secondary: "var(--lb-border-secondary)",
            focus: "var(--lb-border-focus)",
          },
          accent: {
            primary: "var(--lb-accent-primary)",
            secondary: "var(--lb-accent-secondary)",
          },
          state: {
            idle: "var(--lb-state-idle)",
            running: "var(--lb-state-running)",
            success: "var(--lb-state-success)",
            error: "var(--lb-state-error)",
            stale: "var(--lb-state-stale)",
            "stale-upstream": "var(--lb-state-stale-upstream)",
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
