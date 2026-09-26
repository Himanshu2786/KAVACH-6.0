/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#070b14",
          surface: "#0b1325",
          panel: "#101a33",
          border: "rgba(56, 189, 248, 0.15)",
          cyan: "#06b6d4",
          blue: "#38bdf8",
          emerald: "#10b981",
          amber: "#f59e0b",
          rose: "#f43f5e",
          purple: "#a855f7"
        }
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "Consolas", "Monaco", "monospace"],
        sans: ["'Inter'", "system-ui", "-apple-system", "sans-serif"]
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        glow: "0 0 15px rgba(6, 182, 212, 0.25)",
        "glow-red": "0 0 15px rgba(239, 68, 68, 0.25)",
        "glow-green": "0 0 15px rgba(16, 185, 129, 0.25)"
      }
    },
  },
  plugins: [],
}
