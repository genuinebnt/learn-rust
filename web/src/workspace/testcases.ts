// Reads the visible test file so the Tests tab can show every case (input, call, expected) before
// anything runs. Tests are written as `check!(input, call, expected)`; others show just their name.

export interface TestCase {
  name: string;
  /** The human-readable input description (check!'s first argument). */
  input?: string;
  call?: string;
  expected?: string;
  /** Lines before the check!, e.g. `let mut v = ...;`. */
  setup?: string;
}

/** Index just past the string, raw string or char literal starting at `i`, or `i` if there isn't one. */
function skipLiteral(src: string, i: number): number {
  const raw = /^r(#*)"/.exec(src.slice(i, i + 16));
  if (raw) {
    const close = `"${raw[1]}`;
    const end = src.indexOf(close, i + raw[0].length);
    return end < 0 ? src.length : end + close.length;
  }
  if (src[i] === '"') {
    let j = i + 1;
    while (j < src.length && src[j] !== '"') j += src[j] === "\\" ? 2 : 1;
    return j + 1;
  }
  const ch = /^'(\\.|[^\\'])'/.exec(src.slice(i, i + 12));
  return ch ? i + ch[0].length : i;
}

/** Splits `src[from..]` at top-level commas until the bracket that closes the argument list. */
function args(src: string, from: number): { parts: string[]; end: number } {
  const parts: string[] = [];
  let depth = 0;
  let start = from;
  let i = from;
  while (i < src.length) {
    const next = skipLiteral(src, i);
    if (next !== i) {
      i = next;
      continue;
    }
    const c = src[i]!;
    if ("([{".includes(c)) depth++;
    else if (")]}".includes(c)) {
      if (depth === 0) {
        parts.push(src.slice(start, i).trim());
        return { parts: parts.filter(Boolean), end: i };
      }
      depth--;
    } else if (c === "," && depth === 0) {
      parts.push(src.slice(start, i).trim());
      start = i + 1;
    }
    i++;
  }
  return { parts, end: src.length };
}

function unquote(lit: string): string {
  const raw = /^r(#*)"([\s\S]*)"\1$/.exec(lit);
  if (raw) return raw[2]!;
  if (lit.startsWith('"') && lit.endsWith('"')) return lit.slice(1, -1).replace(/\\n/g, "\n").replace(/\\(["\\])/g, "$1");
  return lit;
}

function dedent(s: string): string {
  const lines = s.split("\n").filter((l) => l.trim());
  const indent = Math.min(...lines.map((l) => l.match(/^\s*/)![0].length));
  return lines.map((l) => l.slice(indent)).join("\n");
}

export function testCases(src: string): TestCase[] {
  const out: TestCase[] = [];
  const re = /#\[test\]\s*(?:#\[[^\]]*\]\s*)*fn\s+(\w+)\s*\(\s*\)\s*\{/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(src))) {
    const bodyStart = re.lastIndex;
    const body = args(src, bodyStart);
    const text = src.slice(bodyStart, body.end);
    const at = text.indexOf("check!(");
    const test: TestCase = { name: m[1]! };
    if (at >= 0) {
      const a = args(text, at + "check!(".length).parts;
      if (a.length >= 3) {
        test.input = unquote(a[0]!);
        test.call = a[1];
        test.expected = a[2];
      }
      const setup = dedent(text.slice(0, at));
      if (setup) test.setup = setup;
    }
    out.push(test);
  }
  return out;
}
