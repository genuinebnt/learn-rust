#!/usr/bin/env python3
"""Fills content/dsa/practice.json with the problems the Learn page needs (docs/DSA_LEARN_PAGE_SPEC.md).

    python3 tools/neetcode/problem_catalog.py [--fetch] [--dry-run] [--report FILE]

- Companies come from the public per-company frequency data, restricted to the site's own company set (company_groups of problems.json);
  `--fetch` downloads it (and LeetCode's problem index) to /tmp.
- A problem outside the NeetCode lists is added when it is in technique_problems.json, free, asked by at least one company of the set,
  and carries topic tags.
- Its technique is the one chosen by hand in technique_problems.json (a technique that has a lesson); a problem no technique fits is
  left out.
- Priority outside the lists: MUST (tier A), STRONG (tier B), WARMUP (easy trivia), PRACTICE (the rest).
- A practice problem without any company of the set is retired (practice problems must carry companies and topic tags).
Everything is derived from data; nothing is invented. Idempotent: existing entries keep their order and their companies.
"""
import json
import math
import re
import subprocess
import sys
import tomllib
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DSA = ROOT / "content" / "dsa"
INDEX, TAGS, SITE = Path("/tmp/lc_index.json"), Path("/tmp/lc_tags.json"), Path("/tmp/cw/site_companies.json")
GROUP_WEIGHT = {"Big Tech": 1.0, "Top tech": 0.6, "Databases & infra": 0.5, "Trading": 0.5}
CONCEPT = {"dynamic-programming": 1.0, "graph": 0.9, "breadth-first-search": 0.9, "depth-first-search": 0.9, "tree": 0.9, "binary-tree": 0.9,
           "binary-search-tree": 0.85, "binary-search": 0.9, "two-pointers": 0.9, "sliding-window": 0.9, "hash-table": 0.8, "heap-priority-queue": 0.85,
           "stack": 0.8, "monotonic-stack": 0.8, "backtracking": 0.85, "greedy": 0.8, "linked-list": 0.8, "union-find": 0.7, "topological-sort": 0.8,
           "trie": 0.7, "sweep-line": 0.7, "bit-manipulation": 0.6, "memoization": 0.8, "shortest-path": 0.75, "prefix-sum": 0.7, "monotonic-queue": 0.7,
           "string": 0.55, "array": 0.5, "matrix": 0.55, "math": 0.45, "segment-tree": 0.5, "binary-indexed-tree": 0.5, "design": 0.6, "recursion": 0.6,
           "sorting": 0.55, "simulation": 0.4, "geometry": 0.2, "counting": 0.5}
TRIVIAL = {"array", "string", "hash-table", "math", "sorting", "counting", "simulation", "prefix-sum", "matrix", "counting-sort"}
EXCLUDED = {"database", "shell", "concurrency"}
DIFF = {"easy": "easy", "medium": "medium", "hard": "hard"}


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


def fetch():
    """Downloads LeetCode's index and the per-company frequency files for the site's companies."""
    import csv, io, concurrent.futures as cf
    sys.path.insert(0, str(ROOT / "tools" / "neetcode"))
    import pattern_pages  # noqa: F401  (reuses fetch_index)
    pattern_pages.fetch_index()
    avail = [x["name"] for x in json.loads(sh("curl", "-s", "-m", "30", "https://api.github.com/repos/liquidslr/leetcode-company-wise-problems/contents")) if x["type"] == "dir"]
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    amap = {norm(a): a for a in avail}
    alias = {"towerresearch": "Tower Research Capital", "palantir": "Palantir Technologies"}
    groups = json.loads((DSA / "problems.json").read_text())["company_groups"]
    pick = {}
    for g, cs in groups.items():
        for c in cs:
            f = alias.get(norm(c)) or amap.get(norm(c))
            if f:
                pick[c] = (g, f)
    def get(folder, file):
        url = "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/main/" + urllib.parse.quote(folder) + "/" + urllib.parse.quote(file)
        out = sh("curl", "-s", "-m", "60", url)
        return out if out.startswith("Difficulty") else None
    def one(item):
        name, (g, folder) = item
        return name, g, get(folder, "5. All.csv"), get(folder, "3. Six Months.csv")
    data = {}
    with cf.ThreadPoolExecutor(6) as ex:
        for name, g, allr, six in ex.map(one, pick.items()):
            if not allr:
                continue
            recent = {r["Link"] for r in csv.DictReader(io.StringIO(six))} if six else set()
            data[name] = {"group": g, "rows": [{"link": r["Link"], "freq": float(r["Frequency"] or 0), "recent": r["Link"] in recent}
                                               for r in csv.DictReader(io.StringIO(allr))]}
    SITE.parent.mkdir(parents=True, exist_ok=True)
    SITE.write_text(json.dumps(data))


def words(s):
    return {w for w in re.sub(r"[^a-z0-9 ]", " ", s.lower()).split() if len(w) >= 4}


def main():
    if "--fetch" in sys.argv or not (INDEX.exists() and SITE.exists() and TAGS.exists()):
        fetch()
    dry = "--dry-run" in sys.argv
    idx = {p["slug"]: p for p in json.loads(INDEX.read_text())}
    tag_names = json.loads(TAGS.read_text())
    site = json.loads(SITE.read_text())
    main_file = json.loads((DSA / "problems.json").read_text())
    lists = {p["slug"]: p for p in main_file["problems"]}
    pfile = json.loads((DSA / "practice.json").read_text())
    practice = {p["slug"]: p for p in pfile["problems"]}

    # companies of the site's set, per slug, in the site's format
    comps = defaultdict(list)
    for name, c in site.items():
        for r in c["rows"]:
            slug = r["link"].rstrip("/").split("/problems/")[-1]
            comps[slug].append({"name": name, "group": c["group"], "frequency": round(r["freq"], 1), "recent": r["recent"]})
    for v in comps.values():
        v.sort(key=lambda c: (-c["frequency"], c["name"]))

    def score(slug):
        cs = comps.get(slug, [])
        company = sum(GROUP_WEIGHT.get(c["group"], 0.5) * c["frequency"] / 100 * (1.25 if c["recent"] else 1.0) for c in cs)
        big = sum(1 for c in cs if c["group"] == "Big Tech")
        tags = idx.get(slug, {}).get("tags", [])
        concept = max([CONCEPT.get(t, 0.4) for t in tags] or [0.4])
        return company * (0.5 + 0.5 * concept), big, company

    def priority(slug):
        s, big, _ = score(slug)
        tags = set(idx.get(slug, {}).get("tags", []))
        if idx.get(slug, {}).get("difficulty") == "easy" and tags and tags <= TRIVIAL:
            return "warmup"
        if big >= 5 or s >= 1.4:      # about the top 9% of the problems outside the lists
            return "must"
        if big >= 4 or s >= 0.9:      # the next 18%
            return "strong"
        return "practice"

    # techniques that have a lesson: the lists' techniques and the extras of every lesson file
    tech_pattern = {t["id"]: t["pattern"] for t in main_file["techniques"]}
    tech_name = {t["id"]: t["name"] for t in main_file["techniques"]}
    must_learn = {t["id"]: t["must_learn"] for t in main_file["techniques"]}
    lessons = {}
    for f in DSA.glob("lessons/*.toml"):
        d = tomllib.loads(f.read_text())
        for t in d["technique"]:
            lessons[t["id"]] = {"pattern": d["pattern"], "group": t.get("group")}
        for e in d.get("extra", []):
            lessons[e["id"]] = {"pattern": d["pattern"], "group": e.get("group")}
            tech_pattern[e["id"]] = d["pattern"]
            tech_name[e["id"]] = e["name"]

    # --- the practice problems that stay: they must carry companies and topic tags
    kept, retired = [], []
    for p in pfile["problems"]:
        have = p.get("companies") or comps.get(p["slug"])
        if not have or not p.get("tags"):
            retired.append(p["id"])
            continue
        if not p.get("companies"):
            p["companies"] = comps[p["slug"]]
        kept.append(p)

    # --- the problems to add: the hand-made mapping (technique_problems.json), checked against the rules
    mapping = {k: v for k, v in json.loads((ROOT / "tools/neetcode/technique_problems.json").read_text()).items() if not k.startswith("_")}
    new, skipped = [], []
    for slug, tech in mapping.items():
        if slug in lists or slug in practice:
            continue
        why = None
        if slug not in idx:
            why = "not in LeetCode's index (or untagged)"
        elif idx[slug]["premium"]:
            why = "premium"
        elif set(idx[slug]["tags"]) & EXCLUDED:
            why = "database, shell or concurrency"
        elif not comps.get(slug):
            why = "no company of the site's set asks it"
        elif tech not in lessons:
            why = f"technique {tech} has no lesson"
        if why:
            skipped.append((slug, tech, why))
            continue
        new.append((slug, tech, priority(slug)))

    # --- write
    order = max([p["order"] for p in pfile["problems"]] + [100000]) + 1
    entries = []
    for slug, tech, pr in sorted(new, key=lambda x: (-score(x[0])[0], x[0])):
        p = idx[slug]
        entries.append({
            "id": f"lc-{slug}", "slug": slug, "number": p["id"], "title": p["title"], "difficulty": p["difficulty"],
            "pattern": tech_pattern[tech], "lists": ["practice"], "premium": False,
            "tags": [tag_names.get(t, t) for t in p["tags"]], "companies": comps[slug], "video": None,
            "technique": tech, "order": order, "role": "practice", "practice_of": must_learn.get(tech), "priority": pr,
        })
        order += 1
    for p in kept:
        p["priority"] = priority(p["slug"]) if p["slug"] in comps else p.get("priority", "practice")
    result = {"generated": "2026-10-10", "problems": kept + entries}
    by_pr = Counter(e["priority"] for e in entries)
    print(f"kept {len(kept)} practice problems, retired {len(retired)}, added {len(entries)} (must {by_pr['must']}, strong {by_pr['strong']}, "
          f"warmup {by_pr['warmup']}, practice {by_pr['practice']}), left out {len(skipped)}")
    print("priority of all practice problems:", dict(Counter(p['priority'] for p in result['problems'])))
    if not dry:
        (DSA / "practice.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
        old = {l.strip() for l in (ROOT / "content/retired.txt").read_text().splitlines()}
        add = [r for r in retired if r not in old]
        if add:
            with open(ROOT / "content/retired.txt", "a") as f:
                f.write("\n# 2026-10-10: practice problems that no company of the site's set asks (companies are mandatory).\n" + "\n".join(add) + "\n")
        waived = sorted(p["id"] for p in main_file["problems"] if not p.get("companies") and p["slug"] not in comps)
        (DSA / "no_company.txt").write_text("# NeetCode-list problems that no company of the site's set asks: the only exception to the mandatory company tag.\n"
                                            + "\n".join(waived) + "\n")
    for sl, tech, why in skipped:
        print(f"  left out: {sl} ({tech}): {why}")


main()
