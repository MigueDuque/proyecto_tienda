import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5173,
    watch: {
      // Docker bind mounts on Windows/macOS do not emit filesystem events, so
      // hot reload only works if Vite polls for changes.
      usePolling: true,
      interval: 300,
    },
  },
});
