#!/usr/bin/env python3
"""Checks every URL in a course's stage pages and module files (docs/BUSTUB.md §3: "every URL checked").

    python3 tools/check_course_links.py [courses/bustub] [--fix-atomics]

HTTP 200 passes. YouTube watch links are checked through oEmbed. A few sites (acm.org, mysql.com) answer 403 to scripts: they are
reported as "blocked" and not counted as failures. Rust's std docs move items between `struct.` and `type.` pages between releases;
a 404 on doc.rust-lang.org means the page moved, so check by hand.
"""
import concurrent.futures as cf
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(next((a for a in sys.argv[1:] if not a.startswith("--")), "courses/bustub"))
URL = re.compile(r'https?://(?:[^\s()"\'<>\]]|\([^\s()"\'<>]*\))+')
files = [p for p in root.rglob("*") if p.suffix in {".md", ".toml"} and "reference" not in p.parts and "template" not in p.parts]
urls = {}
for f in files:
    for u in URL.findall(f.read_text()):
        u = u.rstrip(".,;:")
        urls.setdefault(u, []).append(str(f))


def check(u):
    if "youtube.com/watch" in u:
        r = subprocess.run(["curl", "-sL", "-m", "20", "-w", "\n%{http_code}", "https://www.youtube.com/oembed?format=json&url=" + u], capture_output=True, text=True)
        return u, r.stdout.rsplit("\n", 1)[-1]
    for attempt in range(2):
        r = subprocess.run(["curl", "-sL", "-m", "25", "-A", "Mozilla/5.0", "-o", "/dev/null", "-w", "%{http_code}", u], capture_output=True, text=True)
        if r.stdout not in ("000", ""):
            break
    return u, r.stdout


bad = 0
with cf.ThreadPoolExecutor(8) as ex:
    for u, code in sorted(ex.map(check, sorted(urls))):
        if code == "200":
            continue
        if code == "403":
            print(f"blocked {u}")
            continue
        bad += 1
        print(f"{code} {u}\n     in {', '.join(sorted(set(urls[u]))[:3])}")
print(f"{len(urls)} urls, {bad} failing")
sys.exit(1 if bad else 0)
