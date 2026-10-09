#!/usr/bin/env python3
"""Gives every bare `assert!` / `assert_eq!` / `assert_ne!` in the course's stage tests a message that names the behaviour under test.

    python3 tools/add_assert_messages.py [courses/bustub/reference/tests] [--check]

A failing `assert!(ok)` says only "assertion failed: ok". With a message it says which behaviour broke and which expression was false:
`a deleted base with no logs does not exist: expected `reconstruct_tuple(&s, &base, &meta(2333, true), &[]).is_none()``. The behaviour comes
from the test function's name (`s4a_04_a_deleted_base_with_no_logs_does_not_exist`), so names must stay descriptive. Asserts that already have a
message are left alone. `--check` only reports how many are bare (exit 1 if any), for CI or a pre-commit check; the tests are gitignored
(courses/*/reference), so this runs where the reference is.
"""
import re, sys, glob, os

args = [a for a in sys.argv[1:] if not a.startswith("--")]
check = "--check" in sys.argv
root = args[0] if args else "courses/bustub/reference/tests"
ASSERT = re.compile(r"\b(assert|assert_eq|assert_ne)!\(")


def span_of_args(src, start):
    """(index just past the closing paren, number of top-level args) for the macro call whose args start at `start`."""
    i, depth, n, instr, raw = start, 1, 1, False, False
    while depth and i < len(src):
        c = src[i]
        if instr:
            if c == "\\" and not raw:
                i += 1
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == "'" and re.match(r"'(\\.|[^'\\])'", src[i:i + 4]):
            i += len(re.match(r"'(\\.|[^'\\])'", src[i:i + 4]).group(0)) - 1
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 1:
            n += 1
        i += 1
    return i, n


def functions(src):
    """[(name, body_start, body_end, is_test)] of the top-level fns."""
    out = []
    for m in re.finditer(r"^(?:pub )?fn (\w+)[^{;]*\{", src, flags=re.M):
        i, d = m.end(), 1
        while d and i < len(src):
            d += (src[i] == "{") - (src[i] == "}")
            i += 1
        out.append((m.group(1), m.end(), i, "#[test]" in src[max(0, m.start() - 120):m.start()]))
    return out


def behaviour(name):
    name = re.sub(r"^s[0-9a-z]{2,3}_\d\d_", "", name)
    return name.replace("_", " ")


def lit(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("{", "{{").replace("}", "}}")


def process(src):
    fns = functions(src)
    edits = []
    for m in ASSERT.finditer(src):
        # skip macro definitions and anything inside a comment line
        line_start = src.rfind("\n", 0, m.start()) + 1
        if src[line_start:m.start()].lstrip().startswith("//"):
            continue
        end, n = span_of_args(src, m.end())
        need = 2 if m.group(1) != "assert" else 1
        if n > need:
            continue
        expr = src[m.end():end - 1]
        if "$" in expr:
            continue
        owner = next((f for f in fns if f[1] <= m.start() < f[2]), None)
        who = behaviour(owner[0]) if owner else "this check"
        if owner and not owner[3]:
            who = f"in helper `{owner[0]}`"
        if m.group(1) == "assert":
            text = re.sub(r"\s+", " ", expr).strip()
            text = text[:100] + ("..." if len(text) > 100 else "")
            msg = f"{lit(who)}: expected `{lit(text)}`"
        else:
            msg = lit(who)
        tail = expr.rstrip()
        add = f' "{msg}"' if tail.endswith(",") else f', "{msg}"'
        edits.append((m.end() + len(tail), add))
    for pos, add in reversed(edits):
        src = src[:pos] + add + src[pos:]
    return src, len(edits)


total = 0
for f in sorted(glob.glob(os.path.join(root, "stages_*.rs"))):
    src = open(f).read()
    new, n = process(src)
    total += n
    if n and not check:
        open(f, "w").write(new)
print(f"{total} bare assertions {'found' if check else 'given a message'}")
sys.exit(1 if check and total else 0)
