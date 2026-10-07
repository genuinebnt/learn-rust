#!/usr/bin/env python3
"""Fetches LeetCode's whole problem list (number, title, slug, difficulty, Premium, acceptance, topic tags) into
tools/neetcode/cache/problemset.json. The practice lists (practice.py) choose from it.

    python3 tools/neetcode/problemset.py            # uses the cache if present
    python3 tools/neetcode/problemset.py --refresh
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "cache" / "problemset.json"
Q = """query q($skip: Int!, $limit: Int!) { problemsetQuestionList: questionList(categorySlug: "", limit: $limit, skip: $skip, filters: {}) {
  total: totalNum data { questionFrontendId title titleSlug difficulty isPaidOnly acRate topicTags { name } } } }"""


def page(skip, limit=100):
    body = json.dumps({"query": Q, "variables": {"skip": skip, "limit": limit}}).encode()
    req = urllib.request.Request("https://leetcode.com/graphql", data=body, headers={"Content-Type": "application/json", "Referer": "https://leetcode.com/problemset/", "User-Agent": "anneal-dsa-builder"})
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))["data"]["problemsetQuestionList"]
        except Exception as e:  # rate limits: back off and retry
            print("  retry:", e, file=sys.stderr)
            time.sleep(4 * (attempt + 1))
    raise SystemExit("LeetCode did not answer")


def main():
    if CACHE.exists() and "--refresh" not in sys.argv:
        print(len(json.loads(CACHE.read_text())), "problems cached")
        return
    out, skip = {}, 0
    while True:
        r = page(skip)
        for q in r["data"]:
            out[q["titleSlug"]] = {
                "number": int(q["questionFrontendId"]),
                "title": q["title"],
                "difficulty": q["difficulty"],
                "premium": q["isPaidOnly"],
                "acceptance": round(q["acRate"], 1),
                "tags": [t["name"] for t in q["topicTags"]],
            }
        skip += 100
        print(f"  {len(out)}/{r['total']}", file=sys.stderr)
        if skip >= r["total"]:
            break
        time.sleep(0.5)
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(out))
    print(len(out), "problems →", CACHE)


main()
