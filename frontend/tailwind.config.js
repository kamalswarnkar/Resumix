/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: "#1c6e8c",
        accent: "#f2a65a",
      },
    },
  },
  plugins: [],
};
