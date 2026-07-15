/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],

  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2563EB",
          hover: "#1D4ED8",
          foreground: "#FFFFFF",
        },

        secondary: {
          DEFAULT: "#64748B",
          hover: "#475569",
          foreground: "#FFFFFF",
        },

        success: {
          DEFAULT: "#16A34A",
          foreground: "#FFFFFF",
        },

        warning: {
          DEFAULT: "#F59E0B",
          foreground: "#FFFFFF",
        },

        danger: {
          DEFAULT: "#DC2626",
          foreground: "#FFFFFF",
        },

        background: {
          DEFAULT: "#F8FAFC",
          dark: "#0F172A",
        },

        surface: {
          DEFAULT: "#FFFFFF",
          dark: "#1E293B",
        },

        text: {
          primary: "#0F172A",
          secondary: "#475569",
          muted: "#94A3B8",
          inverse: "#F8FAFC",
        },

        border: {
          DEFAULT: "#E2E8F0",
          strong: "#CBD5E1",
        },

        muted: {
          DEFAULT: "#F1F5F9",
          foreground: "#64748B",
        },
      },

      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },

      borderRadius: {
        lg: "0.75rem",
        xl: "1rem",
        "2xl": "1.25rem",
      },

      boxShadow: {
        xs: "0 1px 2px rgba(15,23,42,0.05)",
        sm: "0 2px 6px rgba(15,23,42,0.08)",
        md: "0 6px 16px rgba(15,23,42,0.10)",
        lg: "0 12px 32px rgba(15,23,42,0.12)",
      },

      spacing: {
        18: "4.5rem",
        22: "5.5rem",
        26: "6.5rem",
      },

      transitionTimingFunction: {
        smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },

  plugins: [require("tailwindcss-animate")],
};