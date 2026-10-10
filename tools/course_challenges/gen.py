#!/usr/bin/env python3
"""Generates the challenge stages of a course from the data in packs/*.py.

For every challenge in a pack it writes
  - the stage page and stage.toml under modules/<module>/stages/<slug>/,
  - (when the pack has `src`) the Rust source file under reference/ and its `pub mod` line,
  - (when the pack has `test`) the challenge's tests into reference/tests/<file>, wrapped in `mod ch_<id> { ... }` between marker lines,
    so that running the generator again replaces them instead of adding them twice.

Usage: gen.py [--root COURSE_ROOT] [pack ...]       (default root /tmp/c2/courses/bustub, all packs)
"""
import argparse, glob, importlib.util, json, os, re, sys

HEAD = {
    "build": "A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.",
    "extend": "A challenge: no walkthrough, no hints, no solution. It adds to something you built in this module, using what you learned there. It is extra practice and does not count towards the course.",
    "debug": "A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.",
}


def page(c):
    tier = c["tier"]
    out = [HEAD[tier], ""]
    out += ["## What to fix" if tier == "debug" else "## What to build", "", c["what"].strip(), ""]
    out += ["## Why", "", c["why"].strip(), ""]
    out += ["## The contract", ""] + [f"- {x}" for x in c["contract"]] + [""]
    out += ["## Invariants", "", "These must hold after every step, whatever the input:", ""] + [f"- {x}" for x in c["invariants"]] + [""]
    out += ["## Relations between input and output", "", "How the answer must change when the input changes. The property tests check these on random inputs:", ""] + [f"- {x}" for x in c["relations"]] + [""]
    out += ["## Examples", "", "Worked cases (the tests include them):", "", "```text"] + [x for x in c["examples"]] + ["```", ""]
    out += ["## What the tests check", ""] + [f"- {x}" for x in c["checks"]] + [""]
    done = c.get("done") or ("All the `%s` tests pass, and you can say in one sentence what the bug was." if tier == "debug" else "All the `%s` tests pass.")
    prefix = c["tests"].split("::")[1]
    out += ["## Done when", "", done % prefix if "%s" in done else done, ""]
    return "\n".join(out)


def sorted_mod(path, name):
    """Adds `pub mod name;` after the last `pub mod` line of the file (or at the end), leaving everything else alone."""
    text = open(path).read() if os.path.exists(path) else ""
    decl = f"pub mod {name};"
    lines = text.splitlines()
    if decl in lines:
        return
    last = max([i for i, l in enumerate(lines) if re.match(r"\s*pub mod \w+;", l)], default=-1)
    lines.insert(last + 1, decl)
    open(path, "w").write("\n".join(lines) + "\n")


def put_tests(path, cid, code):
    begin, end = f"// @@ challenge {cid} begin", f"// @@ challenge {cid} end"
    modname = "ch_" + re.sub(r"[^a-z0-9]", "_", cid)
    block = f"{begin}\nmod {modname} {{\n    use proptest::prelude::*;\n\n" + "\n".join(("    " + l if l.strip() else l) for l in code.strip("\n").splitlines()) + f"\n}}\n{end}\n"
    s = open(path).read()
    if begin in s:
        a = s.index(begin)
        b = s.index(end) + len(end) + 1
        s = s[:a] + block + s[b:]
    else:
        s = s.rstrip("\n") + "\n\n" + block
    open(path, "w").write(s)


def load(path):
    spec = importlib.util.spec_from_file_location("pack", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.CH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/tmp/c2/courses/bustub")
    ap.add_argument("packs", nargs="*")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "packs"))
    files = [os.path.join(here, "packs", p if p.endswith(".py") else p + ".py") for p in a.packs] or sorted(p for p in glob.glob(os.path.join(here, "packs", "*.py")) if not os.path.basename(p).startswith("_"))
    n = 0
    for f in files:
        for c in load(f):
            d = os.path.join(a.root, "modules", c["module"], "stages", c["slug"])
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "stage.md"), "w").write(page(c))
            toml = f'id = "{c["id"]}"\ntitle = {json.dumps(c["title"])}\nkind = "challenge"\ndifficulty = "{c["diff"]}"\ntests = {json.dumps([c["tests"]])}\nlearn = {json.dumps(c["learn"])}\nconcepts = []\nconcepts_optional = {json.dumps(c["concepts"])}\n'
            open(os.path.join(d, "stage.toml"), "w").write(toml)
            if "src" in c:
                p = os.path.join(a.root, "reference", c["src"]["path"])
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write(c["src"]["code"].lstrip("\n"))
                sorted_mod(os.path.join(a.root, "reference", os.path.dirname(c["src"]["path"]), "mod.rs"), os.path.basename(c["src"]["path"])[:-3])
            for x in c.get("extra", []):
                p = os.path.join(a.root, "reference", x["path"])
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write(x["code"].lstrip("\n"))
                sorted_mod(os.path.join(a.root, "reference", os.path.dirname(x["path"]), "mod.rs"), os.path.basename(x["path"])[:-3])
            if "test" in c:
                put_tests(os.path.join(a.root, "reference", c["test"]["file"]), c["id"], c["test"]["code"])
            n += 1
    print("challenges written:", n)


if __name__ == "__main__":
    main()
