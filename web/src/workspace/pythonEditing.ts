// How the editor behaves for Python practice problems: indentation that matches what people expect from an editor
// that knows Python, built on @codemirror/lang-python.
//
// What comes from the language package (exercised against a real browser by tools/ui-python-editor*.json): Enter after a
// line ending in `:` indents one level and keeps the level of the surrounding block; a closing bracket dedents its
// line; Tab / Shift-Tab indent and dedent the selected lines; Backspace inside leading whitespace removes a whole
// indent unit; brackets and quotes close in pairs; ⌘/ toggles `#` comments.
//
// What this file adds: typing the `:` of `else`, `elif …`, `except …` or `finally` lines the clause up with the
// `if` / `try` / `for` / `while` it belongs to. The package guesses that from a half-written syntax tree and gets nested
// blocks wrong, so the rule here is explicit and only looks at indentation.
import { EditorSelection, EditorState, Prec, type Extension } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import { python } from "@codemirror/lang-python";

/** Which block openers a clause can close: `else` follows `if`, `elif`, `for`, `while`, `try` and `except`. */
const OPENERS: Record<string, RegExp> = {
    else: /^(if|elif|for|while|try|except)\b/,
    elif: /^(if|elif)\b/,
    except: /^(try|except)\b/,
    finally: /^(try|except|else)\b/,
};

/** Leading whitespace width of a line's text, counting a tab as 4. */
export function indentWidth(text: string): number {
    let n = 0;
    for (const ch of text) {
        if (ch === " ") n += 1;
        else if (ch === "\t") n += 4;
        else break;
    }
    return n;
}

/** The clause keyword of a line being typed (`else`, `elif x`, `except E`, `finally`), when its `:` is about to be typed. */
export function clauseOf(textBeforeColon: string): keyof typeof OPENERS | null {
    const m = /^\s*(else|elif|except|finally)\b/.exec(textBeforeColon);
    if (!m) return null;
    const rest = textBeforeColon.slice(m[0].length);
    if ((m[1] === "else" || m[1] === "finally") && rest.trim() !== "") return null; // `else x:` isn't a clause
    // A colon inside brackets (a slice, a dict) isn't the end of the line.
    let depth = 0;
    for (const ch of rest) {
        if ("([{".includes(ch)) depth++;
        else if (")]}".includes(ch)) depth--;
    }
    return depth > 0 ? null : (m[1] as keyof typeof OPENERS);
}

/**
 * The indentation a clause on line `index` belongs at: that of the nearest opener above it (see [`OPENERS`]) that is at
 * the same level or shallower, looking through the deeper lines of the block just finished. `null` when there isn't one.
 */
export function clauseIndent(lines: string[], index: number, clause: keyof typeof OPENERS): number | null {
    const here = indentWidth(lines[index] ?? "");
    for (let i = index - 1; i >= 0; i--) {
        const text = lines[i] ?? "";
        if (text.trim() === "") continue;
        const w = indentWidth(text);
        if (w > here) continue; // the body of the block that just ended
        if (OPENERS[clause]!.test(text.trim()) && /:\s*(#.*)?$/.test(text.trim())) return w;
        if (w < here) return null; // went out past the current level without meeting an opener (a `def`, say)
    }
    return null;
}

const lineUpClause = EditorView.inputHandler.of((view, from, to, text) => {
    if (text !== ":" || from !== to) return false;
    const line = view.state.doc.lineAt(from);
    const clause = clauseOf(view.state.doc.sliceString(line.from, from));
    if (!clause) return false;
    const lines = view.state.doc.toString().split("\n");
    const target = clauseIndent(lines, line.number - 1, clause);
    const current = /^\s*/.exec(line.text)?.[0] ?? "";
    if (target === null || target >= indentWidth(current)) return false; // only ever dedents; the default insert applies
    const indent = " ".repeat(target);
    view.dispatch({
        changes: [
            { from: line.from, to: line.from + current.length, insert: indent },
            { from, insert: ":" },
        ],
        selection: EditorSelection.cursor(from + 1 + indent.length - current.length),
        userEvent: "input.type",
    });
    return true;
});

/** The Python language with anneal's indentation behaviour. */
export function pythonLanguage(): Extension {
    return [
        python(),
        // Replace the package's re-indent-on-input rule with one that leaves clauses to `lineUpClause`; closing brackets
        // still dedent.
        Prec.high(EditorState.languageData.of(() => [{ indentOnInput: /^\s*[\}\]\)]$/ }])),
        lineUpClause,
    ];
}
