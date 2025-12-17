import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const API_BASE = process.env.VITE_API_BASE || "http://localhost:6969";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to backend during development
      "/api": {
        target: API_BASE,
        changeOrigin: true,
        secure: false
      },
      "/ingest": {
        target: API_BASE,
        changeOrigin: true,
        secure: false
      },
      "/openapi.json": {
        target: API_BASE,
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});