"""Minimal Rust → packet HTML span highlighter (kw, ty, fn, cm, nm, st, lt)."""

from __future__ import annotations

import html
import re

KEYWORDS = {
    "as", "async", "await", "break", "const", "continue", "crate", "dyn", "else",
    "enum", "extern", "false", "fn", "for", "if", "impl", "in", "let", "loop",
    "match", "mod", "move", "mut", "pub", "ref", "return", "self", "Self",
    "static", "struct", "super", "trait", "true", "type", "unsafe", "use",
    "where", "while", "union", "box", "yield", "try",
}

TYPES = {
    "bool", "char", "str", "u8", "u16", "u32", "u64", "u128", "usize",
    "i8", "i16", "i32", "i64", "i128", "isize", "f32", "f64",
    "String", "Vec", "Option", "Result", "Box", "Arc", "Rc", "Mutex", "RwLock",
    "RefCell", "Cell", "Cow", "Path", "PathBuf", "File", "HashMap", "HashSet",
    "BTreeMap", "BTreeSet", "VecDeque", "Instant", "Duration", "Thread",
    "Ordering", "AtomicUsize", "AtomicPtr", "AtomicBool", "AtomicU64",
    "Condvar", "Sender", "Receiver", "JoinHandle", "Pin", "Future",
    "Iterator", "IntoIterator", "FromIterator", "Extend", "Default",
    "Debug", "Clone", "Copy", "Send", "Sync", "Sized", "Drop", "Deref",
    "DerefMut", "Display", "Error", "Read", "Write", "BufRead", "Seek",
}


def highlight(code: str) -> str:
    """Highlight plain Rust source into packet <pre> inner HTML."""
    out: list[str] = []
    i = 0
    n = len(code)

    def emit_text(text: str, cls: str | None = None) -> None:
        esc = html.escape(text, quote=False)
        if cls:
            out.append(f'<span class="{cls}">{esc}</span>')
        else:
            out.append(esc)

    while i < n:
        # line comment
        if code.startswith("//", i):
            j = code.find("\n", i)
            if j < 0:
                j = n
            emit_text(code[i:j], "cm")
            i = j
            continue
        # block comment
        if code.startswith("/*", i):
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            emit_text(code[i:j], "cm")
            i = j
            continue
        # string / raw string / byte string (simplified)
        if code[i] in "\"'":
            quote = code[i]
            j = i + 1
            while j < n:
                if code[j] == "\\":
                    j += 2
                    continue
                if code[j] == quote:
                    j += 1
                    break
                j += 1
            emit_text(code[i:j], "st")
            i = j
            continue
        if code.startswith('b"', i) or code.startswith("br", i) or code.startswith('r"', i) or code.startswith("r#", i):
            # fall through to simpler: treat r#"..."# / "..."
            m = re.match(r'(b?r(#*)")(.*?)\2"', code[i:], re.S)
            if m:
                emit_text(m.group(0), "st")
                i += len(m.group(0))
                continue
            if code.startswith('b"', i):
                j = i + 2
                while j < n:
                    if code[j] == "\\":
                        j += 2
                        continue
                    if code[j] == '"':
                        j += 1
                        break
                    j += 1
                emit_text(code[i:j], "st")
                i = j
                continue
        # char lit
        if code[i] == "'" and i + 2 < n:
            m = re.match(r"'(?:\\.|[^\\])'", code[i:])
            if m:
                emit_text(m.group(0), "st")
                i += len(m.group(0))
                continue
        # lifetime
        if code[i] == "'" and i + 1 < n and (code[i + 1].isalpha() or code[i + 1] == "_"):
            j = i + 1
            while j < n and (code[j].isalnum() or code[j] == "_"):
                j += 1
            emit_text(code[i:j], "lt")
            i = j
            continue
        # number
        if code[i].isdigit():
            j = i
            while j < n and (code[j].isalnum() or code[j] in "._"):
                j += 1
            emit_text(code[i:j], "nm")
            i = j
            continue
        # identifier / keyword
        if code[i].isalpha() or code[i] == "_":
            j = i
            while j < n and (code[j].isalnum() or code[j] == "_"):
                j += 1
            word = code[i:j]
            # function call / definition name
            k = j
            while k < n and code[k] in " \t":
                k += 1
            prev = out[-1] if out else ""
            if word in KEYWORDS:
                emit_text(word, "kw")
            elif word in TYPES or (word[:1].isupper() and word not in KEYWORDS):
                emit_text(word, "ty")
            elif k < n and code[k] == "(" and ("fn</span>" in prev or prev.endswith("fn>") or True):
                # classify as fn if preceded by fn keyword recently or looks like call
                # Look back in raw code
                before = code[max(0, i - 20) : i]
                if re.search(r"\bfn\s*$", before) or (k < n and code[k] == "("):
                    # only mark as fn when defined after `fn ` or clearly a known pattern
                    if re.search(r"\bfn\s*$", before):
                        emit_text(word, "fn")
                    else:
                        emit_text(word, "fn" if word[0].islower() else "ty")
                else:
                    emit_text(word)
            else:
                emit_text(word)
            i = j
            continue
        # punctuation / whitespace
        out.append(html.escape(code[i], quote=False))
        i += 1

    return "".join(out)


def strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


if __name__ == "__main__":
    sample = 'fn main() {\n    assert_eq!(1, 1); // ok\n}\n'
    print(highlight(sample))
