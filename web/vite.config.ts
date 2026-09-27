import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The config runs in Node; only this much of `process` is used (the app's tsconfig has no Node types).
declare const process: { env: Record<string, string | undefined> };

// Dev: the API runs on :8787 (`cargo run -p anneal-api`); Vite proxies /api to it. scripts/dev.sh sets
// ANNEAL_API_PORT and ANNEAL_WEB_PORT when it has to fall back to other ports.
const apiPort = process.env.ANNEAL_API_PORT ?? "8787";

export default defineConfig({
  plugins: [react()],
  server: {
    // 127.0.0.1 explicitly: with plain "localhost", another server on the same port's IPv4 address can shadow Vite.
    host: "127.0.0.1",
    port: Number(process.env.ANNEAL_WEB_PORT ?? 5180),
    strictPort: true,
    // ws: true carries the rust-analyzer WebSocket at /api/lsp/{id}.
    proxy: { "/api": { target: `http://127.0.0.1:${apiPort}`, ws: true } },
  },
});
