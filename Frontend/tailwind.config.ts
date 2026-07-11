import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "var(--ink)",
        panel: "var(--panel)",
        "panel-2": "var(--panel-2)",
        "border-soft": "var(--border-soft)",
        "text-1": "var(--text-1)",
        "text-2": "var(--text-2)",
        amber: "var(--amber)",
        cyan: "var(--cyan)",
        crimson: "var(--crimson)",
        violet: "var(--violet)",
        sage: "var(--sage)"
      },
      fontFamily: {
        display: ["Space Grotesk", "Inter", "system-ui", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "Menlo", "monospace"]
      },
      boxShadow: {
        panel: "0 18px 60px rgba(0, 0, 0, 0.28)"
      }
    }
  },
  plugins: []
};

export default config;
