#!/usr/bin/env python3
"""Fetches LeetCode's current Python 3 starter code for problems into tools/neetcode/cache/templates.json.

    python3 tools/neetcode/templates.py two-sum group-anagrams ...

Solutions must paste into LeetCode, so check_pages.py compares each solution's class and method signature with these.
Premium problems return no snippet; their template is typed by hand in tools/neetcode/premium_templates.json.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "cache" / "templates.json"
Q = "query($s:String!){question(titleSlug:$s){codeSnippets{langSlug code}}}"


def fetch(slug):
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=json.dumps({"query": Q, "variables": {"s": slug}}).encode(),
        headers={"Content-Type": "application/json", "Referer": "https://leetcode.com", "User-Agent": "anneal-dsa-builder"},
    )
    data = json.load(urllib.request.urlopen(req, timeout=30))
    snippets = ((data.get("data") or {}).get("question") or {}).get("codeSnippets") or []
    return next((s["code"] for s in snippets if s["langSlug"] == "python3"), None)


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    for slug in sys.argv[1:]:
        if cache.get(slug):
            continue
        cache[slug] = fetch(slug)
        print(slug, "ok" if cache[slug] else "NO SNIPPET")
        time.sleep(0.5)
    CACHE.write_text(json.dumps(cache, indent=1))


if __name__ == "__main__":
    main()
