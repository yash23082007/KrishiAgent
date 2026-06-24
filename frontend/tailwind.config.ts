import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f4f9f4",
          100: "#e5f2e6",
          200: "#cce5ce",
          500: "#22c55e", // Krishi Green
          600: "#16a34a",
          700: "#15803d",
          900: "#14532d",
        },
        dark: {
          50: "#a1a1aa",
          100: "#f4f4f5",
          800: "#1e1b4b", // deep indigo dark
          900: "#09090b", // slate black
        }
      },
    },
  },
  plugins: [],
};
export default config;
