#!/usr/bin/env python3
"""Builds content/dsa/problems.json: the NeetCode lists as anneal's DSA section.

    python3 tools/neetcode/build.py            # uses tools/neetcode/cache/ for anything already fetched
    python3 tools/neetcode/build.py --refresh  # fetches everything again

Sources:
- NeetCode (neetcode.io's own app bundle): every problem with its pattern, difficulty, video, and which lists it's in
  (Blind 75, NeetCode 150, NeetCode 250, NeetCode All). JavaScript problems are left out.
- LeetCode's public GraphQL API: number, topic tags, premium flag, and "similar questions". Database (SQL) problems
  are left out.
- Company tags, from LeetCode Premium's company lists as published in two public datasets, merged:
  github.com/liquidslr/leetcode-company-wise-problems and github.com/snehasishroy/leetcode-companywise-interview-questions
  (the second covers companies the first doesn't, e.g. Anthropic, Plaid, Figma, Cockroach Labs). Limited to the
  companies in COMPANIES. Elastic, Redis and ClickHouse aren't in either, so they can't be tagged.

Must learn vs practice: every problem is assigned to one technique (the ideas the pattern lessons teach), by hand for
the NeetCode 150 (techniques.py) and for the rest (assign_rest.py), with LeetCode's similar-question links as the
fallback for new problems. The first problem of a technique (NeetCode 150 first, then the 250, then All; a free problem
before a Premium one in the same list; then NeetCode's own order) is its must learn; every other problem using it is practice of that one.
"""
import csv
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

from assign_rest import REST
from techniques import ASSIGN_150, TECHNIQUES

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
OUT = ROOT.parent.parent / "content" / "dsa" / "problems.json"
UA = {"User-Agent": "anneal-dsa-builder (personal study tracker)"}

COMPANIES = {
    "Big Tech": ["Google", "Meta", "Amazon", "Apple", "Netflix", "Microsoft", "Nvidia"],
    "Databases & infra": ["Databricks", "Snowflake", "MongoDB", "Oracle", "Confluent", "Cockroach Labs", "SingleStore", "Couchbase", "Yugabyte", "Cloudera", "Fivetran", "Teradata", "Pure Storage", "Nutanix", "Rubrik", "Datadog", "Cloudflare"],
    "Trading": ["Jane Street", "Citadel", "Two Sigma", "Hudson River Trading", "DE Shaw", "Jump Trading", "Optiver", "IMC", "Tower Research Capital", "Akuna Capital", "Point72", "Squarepoint Capital"],
    "Top tech": ["Stripe", "Airbnb", "Uber", "LinkedIn", "OpenAI", "Anthropic", "Plaid", "Ramp", "Figma", "Coinbase", "Roblox", "Pinterest", "Snap", "Dropbox", "DoorDash", "Lyft", "X", "Bloomberg", "Palantir Technologies", "Robinhood", "Notion", "Scale AI", "ByteDance", "TikTok", "Waymo", "Tesla", "Instacart", "Reddit", "Spotify", "Shopify", "Rippling", "Atlassian", "Salesforce", "Adobe", "Intuit"],
}
DISPLAY = {"Palantir Technologies": "Palantir", "Hudson River Trading": "HRT", "Tower Research Capital": "Tower Research"}
LIST_RANK = {"blind75": 0, "neetcode150": 1, "neetcode250": 2, "all": 3}


def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def cached(name, fetch, refresh):
    path = CACHE / name
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    value = fetch()
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(value))
    return value


def neetcode():
    html = get("https://neetcode.io/practice").decode()
    bundle = re.search(r'src="(main[^"]*\.js)"', html).group(1)
    js = get(f"https://neetcode.io/{bundle}").decode()
    out = []
    for obj in re.findall(r'\{problem:"(?:[^"\\]|\\.)*",[^{}]*\}', js):
        j = re.sub(r'([{,])([A-Za-z_][A-Za-z0-9_]*):', r'\1"\2":', obj).replace(":!0", ":true").replace(":!1", ":false")
        out.append(json.loads(j))
    return out


QUERY = """query q($s: String!) { question(titleSlug: $s) {
  questionFrontendId title difficulty isPaidOnly topicTags { name slug } similarQuestions } }"""


def leetcode(slugs, refresh):
    path = CACHE / "leetcode.json"
    data = json.loads(path.read_text()) if path.exists() and not refresh else {}
    todo = [s for s in slugs if s not in data]
    for i, slug in enumerate(todo):
        body = json.dumps({"query": QUERY, "variables": {"s": slug}}).encode()
        for attempt in range(5):
            try:
                raw = get("https://leetcode.com/graphql", body, {"Content-Type": "application/json", "Referer": f"https://leetcode.com/problems/{slug}/"})
                q = json.loads(raw)["data"]["question"]
                break
            except Exception as e:  # rate limits: back off and retry
                time.sleep(5 * (attempt + 1))
                q = None
        if q is None:
            print(f"  ! no LeetCode data for {slug}", file=sys.stderr)
            continue
        data[slug] = {
            "number": int(q["questionFrontendId"]),
            "title": q["title"],
            "difficulty": q["difficulty"],
            "premium": q["isPaidOnly"],
            "tags": [t["name"] for t in q["topicTags"]],
            "similar": [s["titleSlug"] for s in json.loads(q["similarQuestions"] or "[]")],
        }
        if i % 25 == 0:
            CACHE.mkdir(exist_ok=True)
            path.write_text(json.dumps(data))
            print(f"  LeetCode {i + 1}/{len(todo)}", file=sys.stderr)
        time.sleep(0.35)
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(data))
    return data


# Folder names in the snehasishroy dataset, where they aren't just the lowercased, hyphenated name.
SNEHA = {"Ramp": "ramp-2", "Palantir Technologies": "palantir", "Hudson River Trading": "hrt", "Tower Research Capital": "tower-research", "Snap": "snapchat", "X": "twitter", "Yugabyte": "yugabyte"}


def companies(refresh):
    """{company: {slug: [frequency, recent]}}: the highest frequency either dataset reports, and whether it was asked
    in the last six months according to either."""
    def rows_from(text, recent, rows):
        for r in csv.DictReader(io.StringIO(text)):
            link = r.get("Link") or r.get("URL") or ""
            slug = link.rstrip("/").rsplit("/", 1)[-1]
            if not slug:
                continue
            freq = float(str(r.get("Frequency") or r.get("Frequency %") or 0).rstrip("%") or 0)
            old = rows.get(slug, [0.0, False])
            rows[slug] = [max(old[0], freq), old[1] or recent]

    def fetch():
        out = {}
        for group in COMPANIES.values():
            for c in group:
                rows = {}
                liquid = "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/main/" + urllib.parse.quote(c)
                sneha = "https://raw.githubusercontent.com/snehasishroy/leetcode-companywise-interview-questions/master/" + SNEHA.get(c, c.lower().replace(" ", "-"))
                for base, files in [
                    (liquid, [("5. All.csv", False), ("1. Thirty Days.csv", True), ("2. Three Months.csv", True), ("3. Six Months.csv", True)]),
                    (sneha, [("all.csv", False), ("thirty-days.csv", True), ("three-months.csv", True), ("six-months.csv", True)]),
                ]:
                    for fname, recent in files:
                        try:
                            rows_from(get(f"{base}/{urllib.parse.quote(fname)}").decode(), recent, rows)
                        except Exception:
                            pass
                out[c] = rows
                print(f"  {c}: {len(rows)} problems", file=sys.stderr)
        return out

    return cached("companies.json", fetch, refresh)


def main():
    refresh = "--refresh" in sys.argv
    nc = cached("neetcode.json", neetcode, refresh)
    nc = [p for p in nc if p["pattern"] != "JavaScript"]
    slug_of = lambda p: p["link"].strip("/")
    lc = leetcode([slug_of(p) for p in nc], refresh)
    comp = companies(refresh)

    problems = []
    for p in nc:
        slug = slug_of(p)
        q = lc.get(slug)
        if not q or "Database" in q["tags"]:
            continue  # no SQL
        lists = [k for k in ("blind75", "neetcode150", "neetcode250") if p.get(k)] + ["all"]
        tagged = []
        for group, names in COMPANIES.items():
            for c in names:
                hit = comp.get(c, {}).get(slug)
                if hit:
                    tagged.append({"name": DISPLAY.get(c, c), "group": group, "frequency": round(hit[0], 1), "recent": hit[1]})
        tagged.sort(key=lambda t: (-t["frequency"], t["name"]))
        problems.append({
            "id": f"lc-{slug}",
            "slug": slug,
            "number": q["number"],
            "title": q["title"],
            "difficulty": q["difficulty"].lower(),
            "pattern": p["pattern"],
            "lists": lists,
            "premium": q["premium"],
            "tags": q["tags"],
            "companies": tagged,
            "video": p.get("video") or None,
            "similar": q["similar"],
        })

    # Techniques, then must learn vs practice (tools/neetcode/techniques.py, docs/DSA.md decision 7).
    by_slug = {p["slug"]: p for p in problems}
    position = {slug_of(p): i for i, p in enumerate(nc)}  # NeetCode's own order
    qualify = lambda pattern, key: key if ":" in key else f"{pattern}:{key}"
    technique = {s: qualify(by_slug[s]["pattern"], k) for s, k in {**ASSIGN_150, **REST}.items() if s in by_slug}
    # Anything still unplaced takes the technique of a similar question in the same pattern.
    changed = True
    while changed:
        changed = False
        for p in problems:
            if p["slug"] in technique:
                continue
            near = {s for s in p["similar"] if s in by_slug} | {q["slug"] for q in problems if p["slug"] in q["similar"]}
            votes = Counter(technique[s] for s in near if s in technique and by_slug[s]["pattern"] == p["pattern"])
            if votes:
                technique[p["slug"]] = votes.most_common(1)[0][0]
                changed = True
    unplaced = [p["slug"] for p in problems if p["slug"] not in technique]
    if unplaced:
        sys.exit(f"{len(unplaced)} problems have no technique (add them to tools/neetcode/assign_rest.py): {unplaced[:10]}")
    names = {f"{pattern}:{key}": (pattern, name) for pattern, items in TECHNIQUES.items() for key, name in items}
    unknown = sorted({t for t in technique.values() if t not in names})
    if unknown:
        sys.exit(f"unknown techniques: {unknown}")
    tier = lambda p: 0 if "neetcode150" in p["lists"] else 1 if "neetcode250" in p["lists"] else 2
    first = {}
    for p in problems:
        t = technique[p["slug"]]
        if t not in first or (tier(p), p["premium"], position[p["slug"]]) < (tier(first[t]), first[t]["premium"], position[first[t]["slug"]]):
            first[t] = p
    for p in problems:
        t = technique[p["slug"]]
        p["technique"] = t
        p["order"] = position[p["slug"]]
        if first[t] is p:
            p["role"] = "must_learn"
        else:
            p["role"] = "practice"
            p["practice_of"] = first[t]["id"]
        del p["similar"]
    techniques = sorted(
        ({"id": t, "pattern": names[t][0], "name": names[t][1], "must_learn": p["id"],
          "problems": sum(technique[q["slug"]] == t for q in problems)} for t, p in first.items()),
        key=lambda t: (position[first[t["id"]]["slug"]]))
    problems.sort(key=lambda p: (LIST_RANK[p["lists"][0]], p["pattern"], p["number"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "generated": time.strftime("%Y-%m-%d"),
        "sources": ["neetcode.io", "leetcode.com/graphql", "github.com/liquidslr/leetcode-company-wise-problems"],
        "company_groups": {g: [DISPLAY.get(c, c) for c in names] for g, names in COMPANIES.items()},
        "techniques": techniques,
        "problems": problems,
    }, indent=1) + "\n")
    print(f"{len(problems)} problems → {OUT}")
    print("lists:", Counter(l for p in problems for l in p["lists"]))
    print("roles:", Counter(p["role"] for p in problems), "· must learn by list:",
          Counter(p["lists"][0] for p in problems if p["role"] == "must_learn"))
    print("premium:", sum(p["premium"] for p in problems), "· with a tracked company:", sum(bool(p["companies"]) for p in problems))


main()
