import { keymap } from "@codemirror/view";
import { LSPClient, type Transport, hoverTooltips, jumpToDefinitionKeymap, serverDiagnostics, signatureHelp, signatureKeymap } from "@codemirror/lsp-client";

/** The server shows rust-analyzer this virtual root instead of the real path. */
export const ROOT = "file:///workspace";
export const LIB_URI = `${ROOT}/src/lib.rs`;

export type RaStatus = "off" | "connecting" | "indexing" | "ready" | "error";

export interface RaCallbacks {
  status: (s: RaStatus, detail?: string) => void;
  /** Error and warning counts for src/lib.rs, from rust-analyzer and its cargo check. */
  diagnostics: (errors: number, warnings: number) => void;
}

export interface RaSession {
  client: LSPClient;
  uri: string;
  /** Resolves once the server has answered `initialize`. */
  ready: Promise<void>;
  /** Writes the buffer server-side and triggers rust-analyzer's cargo check. */
  save: (text: string) => void;
  close: () => void;
}

/** Opens a rust-analyzer session for a problem over /api/lsp/{id}. */
export function connectRa(problemId: string, on: RaCallbacks): RaSession {
  const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/lsp/${problemId}`);
  const handlers = new Set<(m: string) => void>();
  let closed = false;
  ws.onmessage = (e) => handlers.forEach((h) => h(String(e.data)));
  const transport: Transport = {
    send: (m) => ws.readyState === WebSocket.OPEN && ws.send(m),
    subscribe: (h) => handlers.add(h),
    unsubscribe: (h) => handlers.delete(h),
  };

  const client = new LSPClient({
    rootUri: ROOT,
    timeout: 15_000,
    extensions: [
      serverDiagnostics(),
      hoverTooltips({ hoverTime: 350 }),
      signatureHelp(),
      keymap.of([...jumpToDefinitionKeymap, ...signatureKeymap]),
      // rust-analyzer reports when indexing is done through this experimental notification.
      { clientCapabilities: { experimental: { serverStatusNotification: true } } },
    ],
    notificationHandlers: {
      "experimental/serverStatus": (_c, params: { quiescent: boolean; health: string; message?: string }) => {
        if (!closed) on.status(params.health === "error" ? "error" : params.quiescent ? "ready" : "indexing", params.message);
        return true;
      },
      // Count, then let serverDiagnostics draw them too.
      "textDocument/publishDiagnostics": (_c, params: { uri: string; diagnostics: { severity?: number }[] }) => {
        if (params.uri === LIB_URI && !closed) {
          on.diagnostics(params.diagnostics.filter((d) => d.severity === 1).length, params.diagnostics.filter((d) => d.severity === 2).length);
        }
        return false;
      },
    },
  });

  on.status("connecting");
  const ready = new Promise<void>((resolve, reject) => {
    ws.onopen = () => {
      client.connect(transport);
      client.initializing.then(() => {
        if (!closed) on.status("indexing");
        resolve();
      }, reject);
    };
    ws.onerror = () => reject(new Error("rust-analyzer connection failed"));
  });
  ws.onclose = (e) => {
    if (!closed) on.status("error", e.reason || "rust-analyzer stopped");
  };
  ready.catch(() => !closed && on.status("error", "couldn't start rust-analyzer"));

  return {
    client,
    uri: LIB_URI,
    ready,
    save: (text) => client.connected && client.notification("anneal/save", { text }),
    close: () => {
      closed = true;
      if (client.connected) client.disconnect();
      ws.close();
    },
  };
}
