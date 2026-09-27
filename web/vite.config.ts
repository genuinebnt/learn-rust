import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: the API runs on :8787 (`cargo run -p anneal-api`); Vite proxies /api to it.
export default defineConfig({
  plugins: [react()],
  server: {
    // 127.0.0.1 explicitly: with plain "localhost", another server on the same port's IPv4 address can shadow Vite.
    host: "127.0.0.1",
    port: 5180,
    strictPort: true,
    // ws: true carries the rust-analyzer WebSocket at /api/lsp/{id}.
    proxy: { "/api": { target: "http://127.0.0.1:8787", ws: true } },
  },
});
