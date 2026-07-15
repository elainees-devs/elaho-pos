/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#2563EB",
        "primary-hover": "#1D4ED8",
        success: "#16A34A",
        warning: "#F59E0B",
        danger: "#DC2626",
        background: "#F8FAFC",
        surface: "#FFFFFF",
        text: {
          primary: "#0F172A",
          secondary: "#64748B",
        },
        border: "#E2E8F0",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

