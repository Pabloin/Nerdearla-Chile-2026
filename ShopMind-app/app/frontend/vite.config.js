import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/invoke": {
        target: process.env.VITE_AGENT_URL || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
