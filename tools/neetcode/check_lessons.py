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


def run_template(key, template, problems):
    """Parses, lints and runs one template; returns its namespace, or None after recording why not."""
    try:
        tree = ast.parse(template)
    except SyntaxError as e:
        problems.append(f"{key}: template syntax error: {e}")
        return None
    long = [l for l in template.splitlines() if len(l) > MAX_LINE]
    if long:
        problems.append(f"{key}: template line over {MAX_LINE} characters (it would scroll sideways): {long[0].strip()[:50]}...")
    missing = undefined_names(tree)
    if missing:
        problems.append(f"{key}: template uses {', '.join(missing)} without defining or importing it")
        return None
    ns = {"__name__": "lesson"}
    exec("from typing import *", ns)
    ns.update(page_tests.PROVIDED_CLASSES)
    try:
        exec(compile(template, key, "exec"), ns)
    except Exception as e:  # noqa: BLE001
        problems.append(f"{key}: template fails to run: {type(e).__name__}: {e}")
        return None
    return ns


def check(path):
    """Returns (problems, tested, lessons, extra ids). An extra's behaviour test is keyed by its id, and a variant's by
    `<id>#<variant name>`; every tab of a lesson is run, so a recursive and an iterative version are both checked."""
    problems, tested, count, extra_ids = [], 0, 0, set()
    doc = tomllib.loads(path.read_text())
    items = [(l, False) for l in doc["technique"]] + [(e, True) for e in doc.get("extra", [])]
    for lesson, is_extra in items:
        tid = lesson["id"]
        count += 1
        if is_extra:
            extra_ids.add(tid)
            if tid in TECHNIQUES:
                problems.append(f"{tid}: an extra can't reuse a technique id")
                continue
        elif tid not in TECHNIQUES:
            problems.append(f"{tid}: isn't a technique")
            continue
        if not lesson["signals"] or not lesson["pitfalls"]:
            problems.append(f"{tid}: needs signals and pitfalls")
        tabs = [(tid, lesson["template"])] + [(f"{tid}#{v['name']}", v["template"]) for v in lesson.get("variant", [])]
        for key, template in tabs:
            ns = run_template(key, template, problems)
            if ns is None:
                continue
            test = lesson_tests.TESTS.get(key)
            if test:
                tested += 1
                try:
                    test(ns)
                except Exception as e:  # noqa: BLE001
                    problems.append(f"{key}: behaviour test fails: {type(e).__name__}: {e}")
    return problems, tested, count, extra_ids


def main():
    files = [Path(a) for a in sys.argv[1:]] or sorted(LESSONS.glob("*.toml"))
    bad, tested, count, extras = [], 0, 0, set()
    for f in files:
        p, t, c, e = check(f)
        bad += [f"{f.name}: {x}" for x in p]
        tested += t
        count += c
        extras |= e
    unknown = {k for k in lesson_tests.TESTS if k.split("#")[0] not in TECHNIQUES | extras}
    bad += [f"lesson_tests.py: {u} isn't a technique" for u in sorted(unknown)]
    for b in bad:
        print("FAIL", b)
    print(f"{count - len(extras)} of {len(TECHNIQUES)} technique lessons and {len(extras)} extras, {tested} templates with a behaviour test, {len(bad)} problems")
    sys.exit(1 if bad else 0)


main()
