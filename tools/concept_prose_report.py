#!/usr/bin/env python3
"""Reports how much of each concept article is prose, and whether it asks the learner anything.

    python3 tools/concept_prose_report.py [courses/bustub/concepts] [--worst N]

Prose here means paragraph lines: not code, tables, bullets, headings or quotes. The owner asked for very high quality prose (docs/COURSE_STANDARDS.md
§11, the `curriculum-review` skill), and the cheapest warning sign is an article that is mostly tables and bullets. The report lists, per article:
words, prose words, prose share, bullet-line share, `## Try it yourself` present, and number of question lines. It never fails; it ranks.
"""
import glob, os, re, sys

argv = sys.argv[1:]
worst = 15
if "--worst" in argv:
    i = argv.index("--worst")
    worst = int(argv[i + 1])
    del argv[i:i + 2]
root = argv[0] if argv else "courses/bustub/concepts"
rows = []
for f in glob.glob(os.path.join(root, "**/*.md"), recursive=True):
    t = open(f).read()
    t = re.sub(r"^---.*?---\n", "", t, count=1, flags=re.S)
    body = re.sub(r"```.*?```", "", t, flags=re.S)
    lines = [l for l in body.split("\n") if l.strip()]
    bullets = sum(1 for l in lines if re.match(r"\s*([-*]|\d+\.) ", l))
    prose = [l for l in lines if not re.match(r"\s*([-*]|\d+\.|#|\||>) ", l)]
    pw = sum(len(l.split()) for l in prose)
    words = len(re.sub(r"```.*?```", "", t, flags=re.S).split())
    rows.append((os.path.basename(f)[:-3], words, pw, pw / max(1, words), bullets / max(1, len(lines)), "## Try it yourself" in t, len(re.findall(r"\?\s*$", body, flags=re.M))))
rows.sort(key=lambda r: r[3])
tot_pw = sum(r[2] for r in rows)
print(f"{len(rows)} articles; prose words {tot_pw}; with a 'Try it yourself' section: {sum(1 for r in rows if r[5])}")
print(f"{'article':52} {'words':>6} {'prose':>6} {'share':>6} {'bullets':>7} try  q")
for r in rows[:worst]:
    print(f"{r[0]:52} {r[1]:6} {r[2]:6} {r[3]:6.0%} {r[4]:7.0%} {'yes' if r[5] else 'no ':3} {r[6]:2}")
