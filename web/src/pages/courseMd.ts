// Markdown for course stages: syntax-highlighted code, colour-coded C/C++ vs Rust tables, and callouts.
//
// Authors write plain markdown. Three conventions give it structure:
//   > [!TIP] An optional title        a GitHub-style alert; types: TIP, NOTE, WARNING, PORT, WHY, BUSTUB
//   **Port rule:** …                  a paragraph that starts with one of the known bold leads becomes a callout
//   a table whose header says "C / C++", "C++", "BusTub" or "Rust", "here"   columns are tinted to match
//   ```svg                            a diagram: inline SVG, optionally starting with a `caption: …` line
//   (raw HTML works too: animated figures, small interactive demos)

import { rust } from "@codemirror/lang-rust";
import { highlightTree, tagHighlighter, tags as t } from "@lezer/highlight";
import { Lexer, Marked, type Tokens } from "marked";

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const span = (cls: string, text: string) => `<span class="${cls}">${esc(text)}</span>`;

// ---------- highlighting ----------

const rustHighlighter = tagHighlighter([
    { tag: [t.keyword, t.self, t.modifier, t.controlKeyword, t.definitionKeyword, t.moduleKeyword, t.operatorKeyword], class: "t-k" },
    { tag: [t.typeName, t.className, t.namespace, t.standard(t.typeName)], class: "t-t" },
    { tag: [t.function(t.variableName), t.function(t.propertyName), t.function(t.definition(t.variableName))], class: "t-f" },
    { tag: [t.string, t.character, t.special(t.string)], class: "t-s" },
    { tag: [t.number, t.bool, t.atom], class: "t-n" },
    { tag: t.macroName, class: "t-m" },
    { tag: [t.labelName, t.special(t.variableName)], class: "t-l" },
    { tag: [t.comment, t.lineComment, t.blockComment, t.docComment], class: "t-c" },
]);

function highlightRust(code: string): string {
    const tree = rust().language.parser.parse(code);
    let out = "";
    let at = 0;
    highlightTree(tree, rustHighlighter, (from, to, cls) => {
        if (from > at) out += esc(code.slice(at, from));
        out += `<span class="${cls}">${esc(code.slice(from, to))}</span>`;
        at = to;
    });
    return out + esc(code.slice(at));
}

const CPP_KEYWORDS = new Set(
    "alignas auto break case catch class const constexpr continue default delete do else enum explicit extern for friend goto if inline mutable namespace new noexcept operator override private protected public register return sizeof static static_assert struct switch template this throw try typedef typename union using virtual volatile while final".split(" "),
);
const CPP_TYPES = new Set("void bool char short int long float double unsigned signed size_t ssize_t off_t string vector unordered_map map set mutex thread atomic optional unique_ptr shared_ptr".split(" "));
const CPP_LITERALS = new Set(["true", "false", "nullptr", "NULL"]);

/** A small C/C++ tokenizer: comments, strings, numbers, preprocessor lines, keywords, types and calls. */
function highlightCpp(code: string): string {
    const re = /(\/\/[^\n]*|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')|(^[ \t]*#[ \t]*\w+)|(\b0x[0-9a-fA-F']+[uUlL]*\b|\b\d[\d']*(?:\.\d+)?[uUlLfF]*\b)|([A-Za-z_]\w*(?:::[A-Za-z_]\w*)*)/gm;
    let out = "";
    let at = 0;
    for (let m = re.exec(code); m; m = re.exec(code)) {
        out += esc(code.slice(at, m.index));
        at = m.index + m[0].length;
        if (m[1]) out += span("t-c", m[0]);
        else if (m[2]) out += span("t-s", m[0]);
        else if (m[3]) out += span("t-m", m[0]);
        else if (m[4]) out += span("t-n", m[0]);
        else {
            const id = m[5] ?? "";
            const last = id.split("::").pop() ?? id;
            const call = /^\s*\(/.test(code.slice(at, at + 3));
            if (CPP_LITERALS.has(id)) out += span("t-n", id);
            else if (CPP_KEYWORDS.has(id)) out += span("t-k", id);
            else if (CPP_TYPES.has(last) || /_t$/.test(last) || /^[A-Z][A-Za-z0-9]*$/.test(last) && !call && /^[A-Z][a-z]/.test(last)) out += span("t-t", id);
            else if (id.includes("::") && !call) out += span("t-t", id);
            else if (call) out += span("t-f", id);
            else out += esc(id);
        }
    }
    return out + esc(code.slice(at));
}

/** Shell sessions: the prompt, the command and its flags. */
function highlightShell(code: string): string {
    return code
        .split("\n")
        .map((line) => {
            const m = /^(\s*)(\$|#)(\s)(.*)$/.exec(line);
            if (!m) return /^\s*#/.test(line) ? span("t-c", line) : esc(line);
            const [, ind, prompt, sp, rest] = m;
            if (prompt === "#") return esc(ind ?? "") + span("t-c", `# ${rest}`);
            const words = (rest ?? "").split(/(\s+)/).map((w, i) => (i === 0 ? span("t-f", w) : /^--?[A-Za-z]/.test(w) ? span("t-n", w) : /^["'].*["']$/.test(w) ? span("t-s", w) : esc(w)));
            return `${esc(ind ?? "")}${span("t-c", prompt ?? "")}${sp ?? ""}${words.join("")}`;
        })
        .join("\n");
}

function highlightToml(code: string): string {
    return code
        .split("\n")
        .map((line) => {
            if (/^\s*#/.test(line)) return span("t-c", line);
            if (/^\s*\[/.test(line)) return span("t-t", line);
            const m = /^(\s*)([\w.-]+)(\s*=\s*)(.*)$/.exec(line);
            if (!m) return esc(line);
            const v = m[4] ?? "";
            return `${esc(m[1] ?? "")}${span("t-f", m[2] ?? "")}${esc(m[3] ?? "")}${/^["']/.test(v) ? span("t-s", v) : /^\d|^(true|false)\b/.test(v) ? span("t-n", v) : esc(v)}`;
        })
        .join("\n");
}

const LANGS: Record<string, { label: string; kind: "rust" | "cpp" | "shell" | "plain"; fn: (c: string) => string }> = {
    rust: { label: "Rust", kind: "rust", fn: highlightRust },
    rs: { label: "Rust", kind: "rust", fn: highlightRust },
    cpp: { label: "C++", kind: "cpp", fn: highlightCpp },
    "c++": { label: "C++", kind: "cpp", fn: highlightCpp },
    c: { label: "C", kind: "cpp", fn: highlightCpp },
    sh: { label: "Shell", kind: "shell", fn: highlightShell },
    bash: { label: "Shell", kind: "shell", fn: highlightShell },
    console: { label: "Shell", kind: "shell", fn: highlightShell },
    toml: { label: "TOML", kind: "plain", fn: highlightToml },
    text: { label: "Text", kind: "plain", fn: esc },
};

/** A diagram: an ```svg fence holds inline SVG (trusted: it comes from the repo). An optional first line `caption: …` becomes the
 *  figure caption. Diagrams use the classes in course.css (box, live, free, hot, ln, dim, grow, …) so they follow the theme. */
function diagram(text: string): string {
    const m = /^caption:\s*(.*)\n/.exec(text);
    const svg = m ? text.slice(m[0].length) : text;
    return `<figure class="cx-diagram">${svg}${m ? `<figcaption>${esc(m[1] ?? "")}</figcaption>` : ""}</figure>`;
}

function codeBlock(text: string, lang: string | undefined): string {
    if (lang?.toLowerCase() === "svg") return diagram(text);
    const code = text.replace(/\n$/, "");
    let spec = lang ? LANGS[lang.toLowerCase().split(/\s/)[0] ?? ""] : undefined;
    // A bare fence that is a shell session ("$ cargo test") reads as one.
    if (!spec && /^\s*\$ /m.test(code)) spec = LANGS.sh;
    const label = spec ? `<span class="cx-lang">${spec.label}</span>` : "";
    const body = spec ? spec.fn(code) : esc(code);
    const kind = spec?.kind ?? "plain";
    return `<figure class="cx-hl ${kind}"><div class="cx-hl-h">${label}<button class="cx-copy" type="button" data-code="${esc(code)}">copy</button></div><pre><code>${body}</code></pre></figure>`;
}

// ---------- callouts ----------

type CalloutKind = "tip" | "note" | "warn" | "port" | "why" | "bustub" | "fit";

const ALERTS: Record<string, [CalloutKind, string]> = {
    TIP: ["tip", "TIP"],
    TRICK: ["tip", "TRICK"],
    NOTE: ["note", "NOTE"],
    WARNING: ["warn", "WATCH OUT"],
    PITFALL: ["warn", "PITFALL"],
    PORT: ["port", "PORTING NOTE"],
    WHY: ["why", "WHY"],
    BUSTUB: ["bustub", "IN BUSTUB"],
};

/** Bold leads at the start of a paragraph that turn it into a callout. */
const LEADS: [RegExp, CalloutKind][] = [
    [/^Port rule\b/i, "port"],
    [/^Where this fits\b/i, "fit"],
    [/^(Pitfall|The classic bug|Careful|Watch out|Don't)\b/i, "warn"],
    [/^Why\b/i, "why"],
    [/^(Tip|Trick|Tips and tricks)\b/i, "tip"],
];

function callout(kind: CalloutKind, title: string, body: string): string {
    return `<aside class="cx-co cx-k-${kind}"><div class="cx-co-t">${esc(title)}</div><div class="cx-co-b">${body}</div></aside>`;
}

// ---------- tables ----------

type Col = "c" | "rust" | "other";

function columnKind(head: string): Col {
    const h = head.trim().toLowerCase();
    if (/^(c\s*\/\s*c\+\+|c\+\+|c|c \(.*\)|bustub|c\+\+ \(.*\))$/.test(h)) return "c";
    if (/^(rust|here|rust \(.*\))$/.test(h)) return "rust";
    return "other";
}

const marked: Marked = new Marked({
    gfm: true,
    renderer: {
        code({ text, lang }: Tokens.Code) {
            return codeBlock(text, lang);
        },
        blockquote(this: { parser: { parse: (t: Tokens.Generic[]) => string } }, { tokens }: Tokens.Blockquote): string {
            const first = tokens[0];
            const m = first?.type === "paragraph" ? /^\[!(\w+)\][ \t]*(.*)(?:\n|$)/.exec((first as Tokens.Paragraph).text) : null;
            const alert = m ? ALERTS[(m[1] ?? "").toUpperCase()] : undefined;
            if (m && alert && first) {
                const rest = (first as Tokens.Paragraph).text.slice(m[0].length).trim();
                const body: string = (m[2] ? `<p><strong>${esc(m[2])}</strong></p>` : "") + this.parser.parse(rest ? [{ type: "paragraph", raw: rest, text: rest, tokens: Lexer.lexInline(rest) } as Tokens.Paragraph, ...tokens.slice(1)] : tokens.slice(1));
                return callout(alert[0], alert[1], body);
            }
            return `<blockquote>${this.parser.parse(tokens)}</blockquote>`;
        },
        paragraph(this: { parser: { parseInline: (t: Tokens.Generic[]) => string } }, { tokens }: Tokens.Paragraph): string {
            const lead = tokens[0];
            if (lead?.type === "strong") {
                const text = (lead as Tokens.Strong).text;
                for (const [re, kind] of LEADS) {
                    if (re.test(text)) {
                        const title = text.replace(/[.:!?]+$/, "").toUpperCase();
                        return callout(kind, title, `<p>${this.parser.parseInline(tokens.slice(1)).replace(/^\s+/, "")}</p>`);
                    }
                }
            }
            return `<p>${this.parser.parseInline(tokens)}</p>\n`;
        },
        table(this: { parser: { parseInline: (t: Tokens.Generic[]) => string } }, token: Tokens.Table): string {
            const heads = token.header.map((h) => h.text);
            const headless = heads.every((h) => !h.trim());
            const kinds: Col[] = heads.map(columnKind);
            const versus = kinds.includes("c") && kinds.includes("rust");
            // In a C++/Rust comparison, a cell that is only a code span is highlighted as that language and gets a copy button.
            const cell = (c: Tokens.TableCell, i = -1) => {
                const only = c.tokens.length === 1 ? c.tokens[0] : undefined;
                const kind = kinds[i];
                if (versus && only?.type === "codespan" && (kind === "c" || kind === "rust")) {
                    const src = only.raw.replace(/^`+ ?/, "").replace(/ ?`+$/, "");
                    return `<code class="src">${(kind === "c" ? highlightCpp : highlightRust)(src)}</code><button class="cx-copy" type="button" data-code="${esc(src)}">copy</button>`;
                }
                return this.parser.parseInline(c.tokens);
            };
            const cls = (i: number) => {
                const k = kinds[i] ?? "other";
                return k === "other" ? (headless && i === 0 ? "key" : "") : k;
            };
            const thead = headless ? "" : `<thead><tr>${token.header.map((h, i) => `<th class="${cls(i)}">${cell(h)}</th>`).join("")}</tr></thead>`;
            const rows = token.rows.map((r) => `<tr>${r.map((c, i) => `<td class="${cls(i)}">${cell(c, i)}</td>`).join("")}</tr>`).join("");
            return `<div class="cx-tbl${versus ? " versus" : ""}"><table>${thead}<tbody>${rows}</tbody></table></div>`;
        },
    },
});

/** Renders stage markdown to HTML (trusted content: it comes from the repo, like the rest of the app's markdown). */
export function renderMd(md: string): string {
    return marked.parse(md, { async: false });
}
