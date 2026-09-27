// Loads a page in headless Chrome and prints the value of a JS expression evaluated in it, e.g.
//   node tools/ui-check.mjs http://127.0.0.1:8787/p/d1-running-sum \
//     "JSON.stringify([...document.querySelectorAll('.ftab')].map(b => b.textContent))" 1280
// For checking layout (widths, overflow, which elements exist) without looking at screenshots.
// CHROME overrides the browser binary.
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, expression = "document.title", width = "1440"] = process.argv.slice(2);
if (!url) {
  console.error("usage: node tools/ui-check.mjs <url> [expression] [width]");
  process.exit(2);
}
const bin = process.env.CHROME ?? (process.platform === "darwin" ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" : "google-chrome");
const port = 9300 + Math.floor(Math.random() * 500);
// Chrome refuses to start as root without --no-sandbox (e.g. in a cloud container).
const rootOnly = process.getuid?.() === 0 ? ["--no-sandbox"] : [];
const chrome = spawn(bin, ["--headless=new", "--disable-gpu", "--hide-scrollbars", ...rootOnly, `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "anneal-ui-"))}`, "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let target;
for (let i = 0; i < 50 && !target; i++) {
  await sleep(200);
  try {
    target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === "page");
  } catch {}
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0;
const pending = new Map();
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m);
    pending.delete(m.id);
  }
};
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });

await send("Emulation.setDeviceMetricsOverride", { width: Number(width), height: 900, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url });
await sleep(3500);
const res = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
console.log(res.result?.exceptionDetails ? res.result.exceptionDetails.exception?.description : res.result?.result?.value);
ws.close();
chrome.kill();
process.exit(0);
