import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#14213d",
        sand: "#f7f3e9",
        ember: "#d96c06",
        fern: "#3c7a57",
        mist: "#d7e3ef",
      },
      boxShadow: {
        card: "0 20px 60px rgba(20, 33, 61, 0.14)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(20, 33, 61, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(20, 33, 61, 0.08) 1px, transparent 1px)",
      },
      fontFamily: {
        display: ["Space Grotesk", "Trebuchet MS", "sans-serif"],
        body: ["IBM Plex Sans", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
