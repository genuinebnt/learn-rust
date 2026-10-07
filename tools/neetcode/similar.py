#!/usr/bin/env python3
"""Fetches LeetCode's "similar questions" for every free problem outside the NeetCode lists into
tools/neetcode/cache/similar.json: {slug: [similar slugs]}. Resumable; practice.py reads it.

    python3 tools/neetcode/similar.py
"""
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "cache"
Q = "query q($s: String!) { question(titleSlug: $s) { similarQuestions } }"


def similar(slug):
    body = json.dumps({"query": Q, "variables": {"s": slug}}).encode()
    req = urllib.request.Request("https://leetcode.com/graphql", data=body, headers={"Content-Type": "application/json", "Referer": f"https://leetcode.com/problems/{slug}/", "User-Agent": "anneal-dsa-builder"})
    for attempt in range(5):
        try:
            q = json.load(urllib.request.urlopen(req, timeout=60))["data"]["question"]
            return [s["titleSlug"] for s in json.loads(q["similarQuestions"] or "[]")]
        except Exception as e:  # rate limits: back off and retry
            time.sleep(4 * (attempt + 1))
    return None


def main():
    problemset = json.loads((CACHE / "problemset.json").read_text())
    neetcode = set(json.loads((CACHE / "leetcode.json").read_text()))
    path = CACHE / "similar.json"
    data = json.loads(path.read_text()) if path.exists() else {}
    todo = [s for s, p in problemset.items() if s not in neetcode and not p["premium"] and "Database" not in p["tags"] and s not in data]
    # A few requests at a time: LeetCode answers in about a second, so one at a time takes the best part of an hour.
    with ThreadPoolExecutor(max_workers=6) as pool:
        for i, (slug, got) in enumerate(zip(todo, pool.map(similar, todo))):
            if got is not None:
                data[slug] = got
            if i % 100 == 0:
                path.write_text(json.dumps(data))
                print(f"  {len(data)} done, {len(todo) - i} to go", file=sys.stderr)
    path.write_text(json.dumps(data))
    print(len(data), "problems →", path)


main()
