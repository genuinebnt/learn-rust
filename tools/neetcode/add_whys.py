"""Adds `time_why` and `space_why` to the approaches of content/dsa/pages/*.toml.

Usage: python3 tools/neetcode/add_whys.py <module.py> ...
Each module defines W = {"<page slug>#<approach index>": (time_why, space_why)}. Approaches that already have the
fields are left alone, so a batch can be run again.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

PAGES = Path(__file__).resolve().parents[2] / "content" / "dsa" / "pages"


def load(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.W


def main(paths):
    whys = {}
    for p in paths:
        whys.update(load(p))
    by_page = {}
    for key, pair in whys.items():
        slug, idx = key.rsplit("#", 1)
        by_page.setdefault(slug, {})[int(idx)] = pair
    changed = 0
    for slug, pairs in by_page.items():
        f = PAGES / f"{slug}.toml"
        text = f.read_text()
        parts = re.split(r"(?m)^(?=\[\[approaches\]\]$)", text)
        out = [parts[0]]
        for i, block in enumerate(parts[1:]):
            if i in pairs and "time_why" not in block:
                tw, sw = pairs[i]
                line = re.search(r'(?m)^space = .*$', block)
                if not line:
                    sys.exit(f"{slug}#{i}: no space line")
                add = f"\ntime_why = {json.dumps(tw, ensure_ascii=False)}\nspace_why = {json.dumps(sw, ensure_ascii=False)}"
                block = block[: line.end()] + add + block[line.end():]
                changed += 1
            out.append(block)
        f.write_text("".join(out))
    print(f"added to {changed} approaches")


if __name__ == "__main__":
    main(sys.argv[1:])
