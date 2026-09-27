#!/usr/bin/env python3
"""Add runnable asserts/tests to all Write + Harden code blocks in part-write.html."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from core_tests import CORE_MAIN
from generate_harden_tests import generate_one
from rust_highlight import highlight, strip_html

ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT.parent / "part-write.html"
EXTRACT_PATH = ROOT / "exercise_extract.json"


def has_check(t: str) -> bool:
    return bool(re.search(r"\bassert(?:_eq|_ne)?!\s*\(", t) or "#[test]" in t)


def extract_check_block(t: str) -> str | None:
    m = re.search(r"#\[cfg\(test\)\][\s\S]*", t)
    if m and has_check(m.group(0)):
        return m.group(0).rstrip()
    mains = list(re.finditer(r"(?:pub\s+)?fn main\b[\s\S]*", t))
    for m in reversed(mains):
        block = m.group(0).rstrip()
        if has_check(block):
            return block
    if has_check(t):
        i = t.find("assert")
        j = t.rfind("fn main", 0, i)
        if j >= 0:
            return t[j:].rstrip()
        j = t.rfind("#[cfg(test)]", 0, i)
        if j >= 0:
            return t[j:].rstrip()
    return None


def replace_or_append_main(code: str, new_main: str) -> str:
    """Replace existing fn main (and trailing comments) or append verification."""
    new_main = new_main.strip()
    if new_main.startswith("#[cfg(test)]"):
        # Remove old main if it's only a demo without asserts; keep impls
        if has_check(code):
            return code
        # Strip trailing fn main without asserts
        code2 = re.sub(r"\nfn main\b[\s\S]*$", "", code.rstrip())
        return code2.rstrip() + "\n\n" + new_main + "\n"

    if re.search(r"\bfn main\b", code):
        # Replace from first fn main to end (demo mains are at end)
        code2 = re.sub(r"\nfn main\b[\s\S]*$", "\n\n" + new_main + "\n", code.rstrip())
        if code2 == code.rstrip():
            # main at start of string
            code2 = re.sub(r"^fn main\b[\s\S]*$", new_main + "\n", code.rstrip())
        return code2 if has_check(code2) else code.rstrip() + "\n\n" + new_main + "\n"
    return code.rstrip() + "\n\n" + new_main + "\n"


def section_bounds(html: str, n: int) -> tuple[int, int]:
    start = html.find(f'<div class="section" id="w{n}">')
    if start < 0:
        raise RuntimeError(f"missing w{n}")
    nxt = html.find('<div class="section" id="w', start + 10)
    end = len(html) if nxt < 0 else nxt
    return start, end


def replace_pre_inner(section: str, pre_index: int, new_plain: str) -> str:
    """Replace the pre_index-th <pre>...</pre> inner HTML in section."""
    pattern = re.compile(r"<pre>(.*?)</pre>", re.S)
    matches = list(pattern.finditer(section))
    if pre_index >= len(matches):
        raise RuntimeError(f"pre index {pre_index} out of range ({len(matches)})")
    m = matches[pre_index]
    highlighted = highlight(new_plain.rstrip() + "\n")
    return section[: m.start(1)] + highlighted + section[m.end(1) :]


def process_core(section: str, n: int, extract: dict) -> str:
    core_end = section.find(f'id="w{n}-harden"')
    if core_end < 0:
        core = section
        rest = ""
    else:
        # keep harden marker with rest
        core = section[:core_end]
        rest = section[core_end:]

    pres = list(re.finditer(r"<pre>(.*?)</pre>", core, re.S))
    if not pres:
        return section

    starter = strip_html(pres[0].group(1))
    solution = strip_html(pres[1].group(1)) if len(pres) > 1 else ""

    # Determine verification block
    verify = CORE_MAIN.get(n)
    if verify is None:
        verify = extract_check_block(solution)
    if verify is None:
        verify = extract.get("sol_check")

    if verify is None:
        print(f"WARN W{n}: no verification block", file=sys.stderr)
        return section

    # Starter
    if not has_check(starter):
        new_starter = replace_or_append_main(starter, verify)
        core = replace_pre_inner(core, 0, new_starter)

    # Solution — refresh indices
    pres = list(re.finditer(r"<pre>(.*?)</pre>", core, re.S))
    if len(pres) > 1:
        solution = strip_html(pres[1].group(1))
        if not has_check(solution):
            new_sol = replace_or_append_main(solution, verify)
            core = replace_pre_inner(core, 1, new_sol)

    return core + rest


def process_harden(section: str, n: int, extract: dict) -> str:
    marker = f'id="w{n}-harden"'
    idx = section.find(marker)
    if idx < 0:
        return section
    head = section[:idx]
    harden = section[idx:]

    for h in extract["hardens"]:
        xid = h["id"]
        card_i = harden.find(f'id="{xid}"')
        if card_i < 0:
            continue
        # find pre after this id, before next card or end
        next_card = harden.find('<div class="card"', card_i + 10)
        chunk_end = next_card if next_card > 0 else len(harden)
        chunk = harden[card_i:chunk_end]
        pre_m = re.search(r"<pre>(.*?)</pre>", chunk, re.S)
        if not pre_m:
            continue
        plain = strip_html(pre_m.group(1))
        if has_check(plain):
            continue
        test = generate_one(n, h)
        new_plain = plain.rstrip() + "\n\n" + test.strip() + "\n"
        new_inner = highlight(new_plain)
        # splice into harden
        abs_start = card_i + pre_m.start(1)
        abs_end = card_i + pre_m.end(1)
        harden = harden[:abs_start] + new_inner + harden[abs_end:]

    return head + harden


def main() -> None:
    html = HTML_PATH.read_text()
    extract_all = json.loads(EXTRACT_PATH.read_text())

    # Rebuild extract sol_check if missing
    for n in range(1, 99):
        start, end = section_bounds(html, n)
        section = html[start:end]
        section = process_core(section, n, extract_all[str(n)])
        section = process_harden(section, n, extract_all[str(n)])
        html = html[:start] + section + html[end:]
        # Re-find bounds because lengths changed — process from end to start instead

    # The above loop is WRONG because replacing section N shifts later offsets.
    # Process from W98 down to W1 instead.
    html = HTML_PATH.read_text()
    for n in range(98, 0, -1):
        start, end = section_bounds(html, n)
        section = html[start:end]
        section = process_core(section, n, extract_all[str(n)])
        section = process_harden(section, n, extract_all[str(n)])
        html = html[:start] + section + html[end:]
        print(f"updated W{n}")

    HTML_PATH.write_text(html)
    print("wrote", HTML_PATH)

    # Recount
    html = HTML_PATH.read_text()
    missing_core = []
    missing_harden = []
    for n in range(1, 99):
        start, end = section_bounds(html, n)
        body = html[start:end]
        if f'id="w{n}-harden"' in body:
            core, hard = body.split(f'id="w{n}-harden"', 1)
        else:
            core, hard = body, ""
        for i, p in enumerate(re.findall(r"<pre>(.*?)</pre>", core, re.S)):
            if not has_check(strip_html(p)):
                missing_core.append(f"w{n}:pre{i}")
        for i, p in enumerate(re.findall(r"<pre>(.*?)</pre>", hard, re.S)):
            if not has_check(strip_html(p)):
                missing_harden.append(f"w{n}-harden:pre{i}")
    print("missing core", len(missing_core), missing_core[:20])
    print("missing harden", len(missing_harden), missing_harden[:20])


if __name__ == "__main__":
    main()
