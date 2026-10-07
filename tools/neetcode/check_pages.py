#!/usr/bin/env python3
"""Checks content/dsa/pages/*.toml (decision 19: solutions paste into LeetCode).

    python3 tools/neetcode/check_pages.py [slug ...]

For every approach: the code parses; it defines the same class and method signatures as LeetCode's Python 3 template
(tools/neetcode/cache/templates.json, fetched by templates.py; Premium problems use premium_templates.json); it doesn't
redefine ListNode, TreeNode or Node; and it passes the checks in page_tests.py. Exits non-zero on any failure.
"""
import ast
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = ROOT.parent.parent / "content" / "dsa" / "pages"
sys.path.insert(0, str(ROOT))
import page_tests  # noqa: E402

TEMPLATES = json.loads((ROOT / "cache" / "templates.json").read_text()) if (ROOT / "cache" / "templates.json").exists() else {}
TEMPLATES.update(json.loads((ROOT / "premium_templates.json").read_text()))
PROVIDED = {"ListNode", "TreeNode", "Node"}


def signatures(source):
    """{class: {method: dump of its arguments and return type}} for the classes in a source."""
    out = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef):
            out[node.name] = {
                f.name: ast.dump(ast.Tuple([f.args, f.returns or ast.Constant(None)], ast.Load()))
                for f in node.body
                if isinstance(f, ast.FunctionDef)
            }
    return out


def check(slug):
    problems = []
    page = tomllib.loads((PAGES / f"{slug}.toml").read_text())
    template = TEMPLATES.get(slug)
    if not template:
        return [f"no LeetCode template for {slug}: run templates.py or add it to premium_templates.json"]
    # The template's method bodies are empty, which doesn't parse: give each one a `pass`.
    stubbed = "".join(line + ("\n        pass" if line.lstrip().startswith("def ") else "") + "\n" for line in template.splitlines())
    want = signatures(stubbed)
    for ap in page.get("approaches", []):
        where = f"{slug} / {ap['name']}"
        try:
            code = ap["code"]
            have = signatures(code)
        except SyntaxError as e:
            problems.append(f"{where}: syntax error: {e}")
            continue
        for cls, methods in want.items():
            for name, sig in methods.items():
                if name.startswith("__"):
                    continue
                if have.get(cls, {}).get(name) != sig:
                    problems.append(f"{where}: {cls}.{name} doesn't match LeetCode's signature")
        for node in ast.parse(code).body:
            if isinstance(node, ast.ClassDef) and node.name in PROVIDED:
                problems.append(f"{where}: redefines {node.name}, which LeetCode provides")
        ns = {}
        try:
            exec(compile(code, where, "exec"), ns)
            page_tests.run(slug, ns)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{where}: fails its checks: {type(e).__name__}: {e}")
        for field in ("name", "label", "idea", "time", "space", "note"):
            if not ap.get(field):
                problems.append(f"{where}: missing {field}")
    for field in ("intuition", "tips"):
        if not page.get(field):
            problems.append(f"{slug}: missing {field}")
    if not page.get("approaches"):
        problems.append(f"{slug}: no approaches")
    return problems


def main():
    slugs = sys.argv[1:] or sorted(p.stem for p in PAGES.glob("*.toml"))
    bad = []
    for slug in slugs:
        bad += check(slug)
    for b in bad:
        print("FAIL", b)
    print(f"{len(slugs)} pages checked, {len(bad)} problems")
    sys.exit(1 if bad else 0)


main()
