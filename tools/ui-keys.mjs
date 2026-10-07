// Drives a page in headless Chrome with real key events, for checking editor behaviour (indentation, brackets, shortcuts).
//   node tools/ui-keys.mjs <url> <steps.json> [width]
// steps.json is a list: {"focus": "css selector"}, {"type": "text"}, {"key": "Enter"} (also Tab, Backspace, Escape,
// ArrowUp/Down/Left/Right, and modifiers: "Shift+Tab", "Mod+a", "Mod+Enter"), {"click": "css selector"},
// {"wait": ms}, {"eval": "js expression"} (result is printed), {"expect": "js expression", "equals": value}.
// Exits non-zero when an expect fails. CHROME overrides the browser binary.
import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, stepsFile, width = "1440"] = process.argv.slice(2);
if (!url || !stepsFile) {
    console.error("usage: node tools/ui-keys.mjs <url> <steps.json> [width]");
    process.exit(2);
}
const steps = JSON.parse(readFileSync(stepsFile, "utf8"));
const bin = process.env.CHROME ?? (process.platform === "darwin" ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" : "google-chrome");
const port = 9300 + Math.floor(Math.random() * 500);
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
const evaluate = async (expression) => {
    const res = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
    if (res.result?.exceptionDetails) throw new Error(res.result.exceptionDetails.exception?.description ?? "evaluation failed");
    return res.result?.result?.value;
};

const KEYS = {
    Enter: { key: "Enter", code: "Enter", vk: 13, text: "\r" },
    Tab: { key: "Tab", code: "Tab", vk: 9 },
    Backspace: { key: "Backspace", code: "Backspace", vk: 8 },
    Escape: { key: "Escape", code: "Escape", vk: 27 },
    ArrowUp: { key: "ArrowUp", code: "ArrowUp", vk: 38 },
    ArrowDown: { key: "ArrowDown", code: "ArrowDown", vk: 40 },
    ArrowLeft: { key: "ArrowLeft", code: "ArrowLeft", vk: 37 },
    ArrowRight: { key: "ArrowRight", code: "ArrowRight", vk: 39 },
    Home: { key: "Home", code: "Home", vk: 36 },
    End: { key: "End", code: "End", vk: 35 },
};
const MODS = { Alt: 1, Ctrl: 2, Mod: process.platform === "darwin" ? 4 : 2, Shift: 8 };

async function press(spec) {
    const parts = spec.split("+");
    const name = parts.pop();
    const modifiers = parts.reduce((m, p) => m | (MODS[p] ?? 0), 0);
    const k = KEYS[name] ?? { key: name, code: /^[a-z]$/i.test(name) ? `Key${name.toUpperCase()}` : name, vk: name.toUpperCase().charCodeAt(0), text: name };
    const withText = modifiers & ~8 ? undefined : k.text; // a shortcut types nothing
    await send("Input.dispatchKeyEvent", { type: withText ? "keyDown" : "rawKeyDown", modifiers, key: k.key, code: k.code, windowsVirtualKeyCode: k.vk, text: withText, unmodifiedText: withText });
    await send("Input.dispatchKeyEvent", { type: "keyUp", modifiers, key: k.key, code: k.code, windowsVirtualKeyCode: k.vk });
}

await send("Emulation.setDeviceMetricsOverride", { width: Number(width), height: 900, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url });
await sleep(3500);

let failed = 0;
for (const step of steps) {
    if (step.focus) await evaluate(`document.querySelector(${JSON.stringify(step.focus)}).focus()`);
    else if (step.click) await evaluate(`document.querySelector(${JSON.stringify(step.click)}).click()`);
    else if (step.type !== undefined) for (const ch of step.type) await send("Input.dispatchKeyEvent", { type: "keyDown", key: ch, text: ch, unmodifiedText: ch });
    else if (step.key) for (let n = 0; n < (step.times ?? 1); n++) await press(step.key);
    else if (step.wait) await sleep(step.wait);
    else if (step.eval) console.log(JSON.stringify(await evaluate(step.eval)));
    else if (step.expect) {
        const got = await evaluate(step.expect);
        const ok = JSON.stringify(got) === JSON.stringify(step.equals);
        if (!ok) failed++;
        console.log(`${ok ? "ok  " : "FAIL"} ${step.label ?? step.expect}${ok ? "" : `\n       expected ${JSON.stringify(step.equals)}\n       got      ${JSON.stringify(got)}`}`);
    }
    await sleep(step.after ?? 40);
}
ws.close();
chrome.kill();
process.exit(failed ? 1 : 0);
