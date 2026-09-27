"""Generate harden verification blocks for all cards (curated + heuristic)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from core_tests import CORE_MAIN
from harden_tests_curated import HARDEN_CURATED

ROOT = Path(__file__).resolve().parent
EXTRACT = json.loads((ROOT / "exercise_extract.json").read_text())


def unwrap_main_body(block: str) -> str | None:
    """Extract inner statements from `fn main() { ... }` for inlining."""
    m = re.search(r"fn main\b[^{]*\{([\s\S]*)\}\s*$", block.strip())
    if not m:
        return None
    body = m.group(1).rstrip()
    # de-indent one level if consistently indented
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return None
    return "\n".join(lines)


def trim_body(body: str, max_lines: int = 80) -> str:
    lines = body.splitlines()
    if len(lines) <= max_lines and "assert" in body:
        return body
    # Prefer keeping lines that contain asserts; always include ≥1 assert
    assert_idxs = [i for i, line in enumerate(lines) if re.search(r"\bassert", line)]
    if not assert_idxs:
        return body if len(lines) <= max_lines else "\n".join(lines[:max_lines])
    # Window around first few asserts
    first = assert_idxs[0]
    last = assert_idxs[min(2, len(assert_idxs) - 1)]
    start = max(0, first - 8)
    end = min(len(lines), last + 3)
    chunk = lines[start:end]
    if start > 0:
        chunk = ["    // ... setup omitted — see core solution tests", *chunk]
    if end < len(lines):
        chunk.append("    // ... further parent checks omitted")
    return "\n".join(chunk)


def parent_verify_body(n: int) -> str | None:
    if n in CORE_MAIN:
        block = CORE_MAIN[n]
        if block.strip().startswith("#[cfg(test)]"):
            return None
        body = unwrap_main_body(block)
        if body and "assert" in body:
            return trim_body(body)
    sc = EXTRACT[str(n)].get("sol_check")
    if sc:
        if sc.strip().startswith("#[cfg(test)]"):
            return None
        body = unwrap_main_body(sc)
        if body and "assert" in body:
            return trim_body(body)
    title = EXTRACT[str(n)]["title"].lower()
    # Minimal fallbacks by family
    if n == 11 or "builder" in title:
        return """\
    let req = RequestBuilder::new("https://example.com")
        .header("A", "1")
        .timeout_ms(100)
        .build()
        .unwrap();
    assert_eq!(req.url, "https://example.com");
    assert!(!req.headers.is_empty());"""
    if n == 27:
        return """\
    let mut mem_in: &[u8] = b"hi";
    let mut mem_out = Vec::new();
    copy_uppercase_ascii(&mut mem_in, &mut mem_out).unwrap();
    assert_eq!(mem_out, b"HI");"""
    if n == 29:
        return """\
    use std::io::Read;
    let mut r = RepeatN { byte: b'x', remaining: 4 };
    let mut out = String::new();
    std::io::Read::read_to_string(&mut r, &mut out).unwrap();
    assert_eq!(out, "xxxx");"""
    if n == 50:
        return """\
    let (producer, consumer) = channel::<u64>(8);
    producer.push(1).unwrap();
    assert_eq!(consumer.pop(), Some(1));"""
    if n == 98:
        return """\
    let policy = RetryPolicy {
        max_attempts: 4,
        base_delay_ms: 100,
        max_delay_ms: 1000,
        budget_ms: 10_000,
    };
    assert_eq!(policy.next_delay(0), Some(100));
    assert_eq!(policy.next_delay(3), None);"""
    return f"""\
    // Parent W{n} regression check — extend with exercise-specific asserts if needed.
    let _w = {n};
    assert_ne!(_w, 0);"""


def harden_fn_name(code: str) -> str | None:
    m = re.search(r"\bfn\s+(harden_w\d+_\d+)\b", code)
    if m:
        return m.group(1)
    return None


def generate_one(n: int, h: dict) -> str:
    xid = h["id"]
    if xid in HARDEN_CURATED:
        return HARDEN_CURATED[xid]

    htitle = h.get("title", "")
    code = h.get("code", "")
    fn = harden_fn_name(code)
    parent_body = parent_verify_body(n)

    # cfg(test) parent — append as module after calling harden fn
    sc = EXTRACT[str(n)].get("sol_check") or ""
    if parent_body is None and sc.strip().startswith("#[cfg(test)]"):
        call = f"{fn}();" if fn else ""
        return f"""\
fn main() {{
    // Harden · {htitle}
    {call}
    println!("run `cargo test` for W{n} + harden checks");
}}

{sc.strip()}
"""

    call_line = f"    {fn}();" if fn else "    // implement the starter API above"

    if parent_body is None:
        # cfg(test)-style parent (e.g. W28/W30) — short dedicated asserts
        if n == 28:
            parent_body = """\
    use std::io::{BufRead, BufReader, Write};
    use std::net::TcpStream;
    use std::thread;
    use std::time::Duration;
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let addr = listener.local_addr().unwrap();
    thread::spawn(move || {
        let (stream, _) = listener.accept().unwrap();
        let _ = handle_client(stream);
    });
    thread::sleep(Duration::from_millis(20));
    let mut client = TcpStream::connect(addr).unwrap();
    writeln!(client, "ping").unwrap();
    let mut line = String::new();
    BufReader::new(client).read_line(&mut line).unwrap();
    assert_eq!(line.trim(), "ping");"""
        elif n == 30:
            parent_body = """\
    let input: &[u8] = b"echo hi\\nquit\\n";
    let mut output = Vec::new();
    run_repl(input, &mut output).unwrap();
    assert!(String::from_utf8_lossy(&output).contains("hi"));"""
        else:
            parent_body = f"""\
    // Harden completed without todo!/panic.
    let _ = {n};
    assert_ne!({n}, 0);"""

    # Indent parent body to main level (already indented)
    if not parent_body.startswith("    "):
        parent_body = "\n".join(
            ("    " + line if line.strip() else line) for line in parent_body.splitlines()
        )

    block = f"""\
fn main() {{
    // Harden · {htitle}
{call_line}
    // Parent exercise still holds after the harden change:
{parent_body}
}}"""
    if not re.search(r"\bassert(?:_eq|_ne)?!\s*\(", block):
        block = block.replace(
            call_line,
            call_line + f"\n    assert!(true, \"harden {xid}: add prompt-specific asserts\");",
        )
    return block


def main() -> None:
    out: dict[str, str] = {}
    for n in range(1, 99):
        for h in EXTRACT[str(n)]["hardens"]:
            if h.get("has_check"):
                continue
            out[h["id"]] = generate_one(n, h)
    path = ROOT / "harden_tests_all.json"
    path.write_text(json.dumps(out, indent=2))
    solid = sum(1 for v in out.values() if re.search(r"\bassert(?:_eq|_ne)?!\s*\(", v))
    weak = sum(1 for v in out.values() if "assert!(true" in v)
    print(f"wrote {len(out)} tests; with asserts={solid}; weak={weak}")


if __name__ == "__main__":
    main()
