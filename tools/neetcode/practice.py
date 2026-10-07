#!/usr/bin/env python3
"""Chooses the practice problems (decision 24): about four free LeetCode problems per technique, from outside the
NeetCode lists, written to content/dsa/practice.json in the same shape as problems.json.

    python3 tools/neetcode/problemset.py && python3 tools/neetcode/similar.py     # once: fetch the data
    python3 tools/neetcode/practice.py [--show Pattern]

How a candidate is matched to a technique:
- LeetCode's "similar questions" links, in both directions, between the candidate and the technique's problems (strong);
- topic tags it shares with the technique's problems, weighted by how rare the tag is (weaker);
- popularity: how many of the tracked companies ask it, and whether recently (a tie-breaker that favours the problems
  interviews actually use).
Each problem goes to one technique. A technique keeps its best four, spread over difficulties (at most two Hard, and at
least one Easy or Medium), and fewer when little matches well. `PICKS` and `DROP` below override the choice by hand.
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
REPO = ROOT.parent.parent
OUT = REPO / "content" / "dsa" / "practice.json"
PER_TECHNIQUE = 4
MIN_SCORE = 2.0
FILL_SCORE = 1.3

# Hand overrides, reviewed against the printed lists: {technique id: [slugs to include first]} and slugs never to use.
PICKS: dict[str, list[str]] = {}
DROP: set[str] = set()

# A candidate is only considered for a pattern when it carries one of the pattern's topic tags, or LeetCode links it to one
# of the pattern's problems. Without this, tag overlap alone drifts ("Richest Customer Wealth" as a trie-on-grid problem).
PATTERN_TAGS = {
    "Arrays & Hashing": {"Hash Table", "Prefix Sum", "Counting", "Array", "String", "Design"},
    "Two Pointers": {"Two Pointers"},
    "Stack": {"Stack", "Monotonic Stack"},
    "Binary Search": {"Binary Search"},
    "Sliding Window": {"Sliding Window", "Monotonic Queue"},
    "Linked List": {"Linked List", "Doubly-Linked List"},
    "Trees": {"Tree", "Binary Tree", "Binary Search Tree"},
    "Tries": {"Trie"},
    "Heap / Priority Queue": {"Heap (Priority Queue)"},
    "Backtracking": {"Backtracking"},
    "Graphs": {"Graph", "Depth-First Search", "Breadth-First Search", "Union Find", "Topological Sort"},
    "Advanced Graphs": {"Shortest Path", "Minimum Spanning Tree", "Graph", "Strongly Connected Component"},
    "1-D Dynamic Programming": {"Dynamic Programming"},
    "2-D Dynamic Programming": {"Dynamic Programming"},
    "Greedy": {"Greedy"},
    "Intervals": {"Sorting", "Line Sweep", "Greedy"},
    "Math & Geometry": {"Math", "Geometry", "Matrix", "Number Theory", "Simulation"},
    "Bit Manipulation": {"Bit Manipulation"},
}

SKIP_TAGS = {"Database", "Shell", "Concurrency", "JavaScript", "Interactive", "Brainteaser"}


def load():
    problems = json.loads((REPO / "content/dsa/problems.json").read_text())
    return (
        problems,
        json.loads((CACHE / "problemset.json").read_text()),
        json.loads((CACHE / "similar.json").read_text()),
        json.loads((CACHE / "leetcode.json").read_text()),
        json.loads((CACHE / "companies.json").read_text()),
    )


def main():
    problems, problemset, similar, seed_similar, company_rows = load()
    seeds = {p["slug"]: p for p in problems["problems"]}
    technique_of = {p["slug"]: p["technique"] for p in problems["problems"]}
    techniques = {t["id"]: t for t in problems["techniques"]}
    group_of = {c: g for g, names in problems["company_groups"].items() for c in names}

    pool = {
        s: p
        for s, p in problemset.items()
        if s not in seeds and not p["premium"] and not (set(p["tags"]) & SKIP_TAGS) and s in similar and s not in DROP
    }

    # tag rarity over the whole problem set, and the tags each technique's problems carry
    tag_count = Counter(t for p in problemset.values() for t in p["tags"])
    idf = {t: math.log(len(problemset) / n) for t, n in tag_count.items()}
    technique_tags: dict[str, Counter] = defaultdict(Counter)
    for slug, p in seeds.items():
        for t in p["tags"]:
            technique_tags[technique_of[slug]][t] += 1
    technique_size = Counter(technique_of.values())

    # links between a candidate and a technique's problems, from either side
    links: dict[tuple[str, str], int] = Counter()
    for seed, info in seed_similar.items():
        if seed not in seeds:
            continue
        for other in info["similar"]:
            if other in pool:
                links[(other, technique_of[seed])] += 1
    for cand, others in similar.items():
        if cand not in pool:
            continue
        for other in others:
            if other in seeds:
                links[(cand, technique_of[other])] += 1

    def asked_by(slug):
        out = []
        for company, rows in company_rows.items():
            if slug in rows:
                freq, recent = rows[slug]
                out.append({"name": company, "group": group_of.get(company, "Top tech"), "frequency": round(freq, 1), "recent": bool(recent)})
        out.sort(key=lambda c: (-c["frequency"], c["name"]))
        return out

    popularity = {}
    for slug in pool:
        cs = asked_by(slug)
        popularity[slug] = math.log1p(len(cs)) * 0.55 + 0.35 * any(c["recent"] for c in cs) + (max((c["frequency"] for c in cs), default=0) / 100) * 0.4

    scored = []  # (score, slug, technique)
    by_pair: dict[tuple[str, str], tuple[float, int]] = {}
    for slug, p in pool.items():
        tags = [t for t in p["tags"] if idf.get(t, 0) > 1.7]  # generic tags like Array, String and Hash Table say little
        norm = sum(idf[t] for t in tags) or 1.0
        for tid, t in techniques.items():
            overlap = sum(idf[x] for x in tags if technique_tags[tid][x] / technique_size[tid] > 0.15) / norm
            link = links.get((slug, tid), 0)
            if not (set(p["tags"]) & PATTERN_TAGS.get(t["pattern"], set())):
                continue
            score = 2.2 * min(link, 3) + 1.6 * overlap + popularity[slug]
            scored.append((score, slug, tid))
            by_pair[(slug, tid)] = (score, link)
    scored.sort(reverse=True)

    # a problem only teaches one technique: its best match (it must be a real match: a link or a shared specific tag)
    best: dict[str, tuple[float, str]] = {}
    for score, slug, tid in scored:
        if slug not in best and (by_pair[(slug, tid)][1] or score >= MIN_SCORE):
            best[slug] = (score, tid)
    chosen: dict[str, list[str]] = defaultdict(list)
    for tid, picks in PICKS.items():
        chosen[tid] = [s for s in picks if s in pool]
    taken = {s for v in chosen.values() for s in v}
    by_technique: dict[str, list[tuple[float, str]]] = defaultdict(list)
    for slug, (score, tid) in best.items():
        if slug not in taken and score >= MIN_SCORE:
            by_technique[tid].append((score, slug))
    for tid, cands in by_technique.items():
        cands.sort(reverse=True)
        picked = chosen[tid]
        hard = sum(pool[s]["difficulty"] == "Hard" for s in picked)
        for _, slug in cands:
            if len(picked) >= PER_TECHNIQUE:
                break
            if pool[slug]["difficulty"] == "Hard" and hard >= 1:
                continue
            hard += pool[slug]["difficulty"] == "Hard"
            picked.append(slug)
        if picked and all(pool[s]["difficulty"] == "Hard" for s in picked):
            easier = [s for _, s in cands if pool[s]["difficulty"] != "Hard" and s not in picked]
            if easier:
                picked[-1] = easier[0]

    # techniques that came up short borrow the best unused problems of their own pattern
    used = {s for v in chosen.values() for s in v}
    for tid, t in techniques.items():
        if len(chosen[tid]) >= PER_TECHNIQUE:
            continue
        spare = sorted(((sc, sl) for sc, sl, ti in scored if ti == tid and sl not in used and sc >= FILL_SCORE), reverse=True)
        for _, slug in spare:
            if len(chosen[tid]) >= PER_TECHNIQUE:
                break
            if pool[slug]["difficulty"] == "Hard" and any(pool[x]["difficulty"] == "Hard" for x in chosen[tid]):
                continue
            chosen[tid].append(slug)
            used.add(slug)

    out = []
    rank = {"Easy": 0, "Medium": 1, "Hard": 2}
    technique_order = {t["id"]: i for i, t in enumerate(problems["techniques"])}
    for tid in sorted(chosen, key=lambda t: technique_order[t]):
        t = techniques[tid]
        for slug in sorted(chosen[tid], key=lambda s: (rank[pool[s]["difficulty"]], pool[s]["number"])):
            p = pool[slug]
            out.append({
                "id": f"lc-{slug}",
                "slug": slug,
                "number": p["number"],
                "title": p["title"],
                "difficulty": p["difficulty"].lower(),
                "pattern": t["pattern"],
                "lists": ["practice"],
                "premium": False,
                "tags": p["tags"],
                "companies": asked_by(slug),
                "video": None,
                "technique": tid,
                "order": 100000 + technique_order[tid] * 10 + len([o for o in out if o["technique"] == tid]),
                "role": "practice",
                "practice_of": t["must_learn"],
            })
    OUT.write_text(json.dumps({"generated": problems["generated"], "problems": out}, indent=1) + "\n")

    per_pattern = Counter(p["pattern"] for p in out)
    print(f"{len(out)} practice problems for {len({p['technique'] for p in out})} of {len(techniques)} techniques → {OUT}")
    for pattern, n in per_pattern.items():
        print(f"  {pattern:26} {n}")
    show = sys.argv[sys.argv.index("--show") + 1] if "--show" in sys.argv else None
    if show:
        for t in problems["techniques"]:
            if t["pattern"] != show:
                continue
            mine = [p for p in out if p["technique"] == t["id"]]
            print(f"\n{t['id']}  — {t['name']}   (learn: {t['must_learn'][3:]})")
            for p in mine:
                print(f"    {p['difficulty'][0].upper()} #{p['number']:<5} {p['title']}   [{', '.join(p['tags'][:4])}]")
            if not mine:
                print("    (nothing matched well)")


main()
