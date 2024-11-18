import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/pluviometria/",
  server: {
    watch: {
      usePolling: true,
    },
    cors: false, 
  },
  resolve: {
    alias: {
      styles: './src/theme/styles.js',
    },
  },
});