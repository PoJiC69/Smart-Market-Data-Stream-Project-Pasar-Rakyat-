import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const API_BASE = process.env.VITE_API_BASE || "http://localhost:6969";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to backend during development.
      // Adjust paths as needed (e.g. /ingest, /api/*, /openapi.json)
      "/api": {
        target: API_BASE,
        changeOrigin: true,
        secure: false,
      },
      "/ingest": {
        target: API_BASE,
        changeOrigin: true,
        secure: false,
      },
      "/openapi.json": {
        target: API_BASE,
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});