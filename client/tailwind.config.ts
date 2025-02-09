import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  safelist: [
    "bg-gray-50",
    "text-gray-500",
    "text-gray-900",
    "border-gray-200",
    "border-gray-300",
    "ring-primary-500",
    "border-primary-500",
    {
      pattern: /^(bg|text|border|ring)-primary-\d00/,
    },
    {
      pattern: /^(bg|text|border|ring)-gray-\d00/,
    },
    "flex",
    "flex-col",
    "flex-1",
    "overflow-y-auto",
    "p-4",
    "bg-white",
    "border-t",
    "gap-4",
    "px-4",
    "py-3",
    "rounded-lg",
    "border",
    "focus:ring-2",
    "focus:ring-primary-500/50",
    "focus:border-primary-500",
    "transition-colors",
    {
      pattern: /^(p|px|py|m|mx|my)-\d+$/,
    },
    {
      pattern: /^(flex|grid|gap)-\d+$/,
    },
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      colors: {
        primary: {
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7e22ce",
          800: "#6b21a8",
          900: "#581c87",
        },
        secondary: {
          50: "#fff7ed",
          100: "#ffedd5",
          200: "#fed7aa",
          300: "#fdba74",
          400: "#fb923c",
          500: "#f97316",
          600: "#ea580c",
          700: "#c2410c",
          800: "#9a3412",
          900: "#7c2d12",
        },
      },
      animation: {
        fadeIn: "fadeIn 0.3s ease-in-out",
        slideUp: "slideUp 0.4s ease-out",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
