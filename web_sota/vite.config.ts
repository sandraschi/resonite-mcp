import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 10714,
    host: "127.0.0.1",
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:10715',
        changeOrigin: true,
      },
      '/resonite': {
        target: 'http://127.0.0.1:10715',
        changeOrigin: true,
      },
      '/rl': {
        target: 'http://127.0.0.1:10715',
        changeOrigin: true,
      }
    }
  },
});
