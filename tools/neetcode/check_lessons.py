#!/usr/bin/env python3
"""Checks content/dsa/lessons/*.toml (the pattern lessons, decision 6).

    python3 tools/neetcode/check_lessons.py [pattern-file ...]

For every technique lesson: the template parses, uses no name it never defines or imports (so a missing `import` shows up
here, not when pasted into LeetCode), and runs its behaviour test in lesson_tests.py when there is one. The signals and
pitfalls must be non-empty. Reports how many of the 162 techniques have a lesson and how many templates have a test.
Exits non-zero on any failure.
"""
import ast
import builtins
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LESSONS = ROOT.parent.parent / "content" / "dsa" / "lessons"
sys.path.insert(0, str(ROOT))
import lesson_tests  # noqa: E402
import page_tests  # noqa: E402

TECHNIQUES = {t["id"] for t in json.loads((ROOT.parent.parent / "content" / "dsa" / "problems.json").read_text())["techniques"]}
# LeetCode provides these classes and `from typing import *`.
MAX_LINE = 76
BUILTINS = set(dir(builtins)) | {"Node", "ListNode", "TreeNode"}


def undefined_names(tree):
    """Names that are read but never bound anywhere in the template, imported, or builtin."""
    bound = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                bound.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, ast.alias):
            bound.add((node.asname or node.name).split(".")[0])
    return sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} - bound - BUILTINS)


def check(path):
    problems, tested, count = [], 0, 0
    doc = tomllib.loads(path.read_text())
    for lesson in doc["technique"]:
        tid = lesson["id"]
        count += 1
        if tid not in TECHNIQUES:
            problems.append(f"{tid}: isn't a technique")
            continue
        if not lesson["signals"] or not lesson["pitfalls"]:
            problems.append(f"{tid}: needs signals and pitfalls")
        try:
            tree = ast.parse(lesson["template"])
        except SyntaxError as e:
            problems.append(f"{tid}: template syntax error: {e}")
            continue
        long = [l for l in lesson["template"].splitlines() if len(l) > MAX_LINE]
        if long:
            problems.append(f"{tid}: template line over {MAX_LINE} characters (it would scroll sideways): {long[0].strip()[:50]}...")
        missing = undefined_names(tree)
        if missing:
            problems.append(f"{tid}: template uses {', '.join(missing)} without defining or importing it")
            continue
        ns = {"__name__": "lesson"}
        exec("from typing import *", ns)
        ns.update(page_tests.PROVIDED_CLASSES)
        try:
            exec(compile(lesson["template"], tid, "exec"), ns)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{tid}: template fails to run: {type(e).__name__}: {e}")
            continue
        test = lesson_tests.TESTS.get(tid)
        if test:
            tested += 1
            try:
                test(ns)
            except Exception as e:  # noqa: BLE001
                problems.append(f"{tid}: behaviour test fails: {type(e).__name__}: {e}")
    return problems, tested, count


def main():
    files = [Path(a) for a in sys.argv[1:]] or sorted(LESSONS.glob("*.toml"))
    bad, tested, count = [], 0, 0
    for f in files:
        p, t, c = check(f)
        bad += [f"{f.name}: {x}" for x in p]
        tested += t
        count += c
    unknown = set(lesson_tests.TESTS) - TECHNIQUES
    bad += [f"lesson_tests.py: {u} isn't a technique" for u in sorted(unknown)]
    for b in bad:
        print("FAIL", b)
    print(f"{count} of {len(TECHNIQUES)} lessons, {tested} with a behaviour test, {len(bad)} problems")
    sys.exit(1 if bad else 0)


main()
