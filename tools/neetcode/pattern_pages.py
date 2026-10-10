#!/usr/bin/env python3
"""Builds the grouped pattern pages (docs/DSA.md decision 32) for every topic from docs/DSA_*_PATTERNS.md and LeetCode's own index.

    python3 tools/neetcode/pattern_pages.py [--fetch] [--dry-run] [pattern ...]

For each topic document (a numbered list of groups, each a `;`-separated list of techniques with example problems in parentheses):
  - the groups become the page's `groups`;
  - an item that names a problem in the NeetCode lists is already taught by that problem's technique: it is not listed, and it votes
    for the group of that technique;
  - any other item is `[[listed]]`, with the LeetCode problems it names (exact title match against LeetCode's index, which `--fetch`
    downloads: slug, number, difficulty, paid) and, when an existing lesson mentions its key words, a pointer to that lesson;
  - each group gets LeetCode topic tags (`group_tags`) where its name says which.
Hand-written parts are kept: `groups` of a file that already has them, a technique's own `group`, every `[[extra]]`.
Nothing is invented: a problem is attached only when its title is in LeetCode's index.
"""
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
LESSONS = ROOT / "content" / "dsa" / "lessons"
INDEX = Path("/tmp/lc_index.json")
TAGS = Path("/tmp/lc_tags.json")

DOCS_TO_PATTERNS = {
    "ARRAYS_HASHING": ["Arrays & Hashing"], "BACKTRACKING": ["Backtracking"], "BINARY_SEARCH": ["Binary Search"],
    "BIT_MANIPULATION": ["Bit Manipulation"], "DP": ["1-D Dynamic Programming", "2-D Dynamic Programming"],
    "GRAPH": ["Graphs", "Advanced Graphs"], "GREEDY": ["Greedy"], "HEAP": ["Heap / Priority Queue"], "INTERVALS": ["Intervals"],
    "LINKED_LIST": ["Linked List"], "MATH_GEOMETRY": ["Math & Geometry"], "SLIDING_WINDOW": ["Sliding Window"], "STACK": ["Stack"],
    "TREES": ["Trees"], "TRIES": ["Tries"], "TWO_POINTERS": ["Two Pointers"],
}
# group title -> LeetCode topic tags (every slug is checked against LeetCode's tag list). Reviewed by hand: a group is only tagged when
# the tag names what the group is about. Groups that are not listed have no tag.
GROUP_TAGS = {
    # Arrays & Hashing
    "Frequency counting": ["counting"], "Prefix sums with a map": ["prefix-sum"], "Difference arrays": ["prefix-sum"],
    "Prefix / suffix products and aggregates": ["prefix-sum"], "Counting and bucket tricks": ["counting-sort", "bucket-sort"],
    "Design with hash maps": ["design"], "Hashing structures": ["hash-function"], "Sorting-based approaches": ["sorting"],
    "Matrix traversal and transform": ["matrix"], "Simulation": ["simulation"], "Majority element": ["counting"],
    # Backtracking
    "Subsets, combinations and permutations": ["backtracking"], "Grid and word search with visited state": ["matrix", "backtracking"],
    "Bitmask state": ["bitmask"], "Meet in the middle": ["meet-in-the-middle"], "Game-tree search": ["game-theory", "minimax-algorithm"],
    "Iterative generation": ["enumeration"], "Backtracking versus DP boundary": ["memoization"],
    # Binary search
    "Kth element problems": ["quickselect", "heap-priority-queue"], "Weighted random pick": ["randomized"],
    "Binary search + two pointers": ["binary-search"], "Pointer + binary search": ["binary-search"],
    "Counting-based search": ["binary-search"], "Search on the answer (minimise the max / maximise the minimum)": ["binary-search"],
    "Classic boundaries": ["binary-search"], "Rotated arrays": ["binary-search"], "Peaks and turning points": ["binary-search"],
    "2-D matrices": ["matrix", "binary-search"], "Unknown size / exponential search": ["interactive"], "Oracle / interactive": ["interactive"],
    # Bit manipulation
    "Single-number tricks": ["bit-manipulation"], "XOR tricks": ["bit-manipulation"], "Masks, shifts and fields": ["bit-manipulation"],
    "Bitmask subsets and bitmask DP": ["bitmask"], "Bit-level greedy and tries": ["trie", "bit-manipulation"], "Range AND / OR": ["bit-manipulation"],
    "Gray code": ["bit-manipulation"], "Bit manipulation for sets": ["bitmask"], "Sieve and bitset algorithms": ["number-theory"],
    # DP
    "Bitmask DP": ["bitmask"], "Probability and expected value": ["probability-and-statistics"], "Game and minimax DP": ["game-theory", "minimax-algorithm"],
    "Counting DP": ["combinatorics"], "Prefix-sum and monotonic-queue optimisation": ["monotonic-queue", "prefix-sum"],
    "Divide and conquer, Knuth and convex hull trick": ["divide-and-conquer"], "Memoisation versus tabulation": ["memoization"],
    "Tree DP": ["binary-tree"], "Grid and path DP": ["matrix"], "Digit DP": ["math"],
    # Graphs
    "Topological sort and dependencies": ["topological-sort"], "Union-find (DSU)": ["union-find"], "Shortest paths": ["shortest-path"],
    "Minimum spanning trees": ["minimum-spanning-tree"], "Connectivity and graph decomposition": ["strongly-connected-component", "biconnected-component"],
    "Eulerian and Hamiltonian": ["eulerian-circuit"], "Advanced connectivity and offline algorithms": ["biconnected-component", "union-find"],
    "Traversal": ["breadth-first-search", "depth-first-search"], "Tree algorithms": ["binary-tree"], "Backtracking and enumeration": ["backtracking"],
    "Cycle detection and graph properties": ["graph"], "Graph modeling and state-space search": ["graph"],
    # Greedy
    "Heap-assisted greedy": ["heap-priority-queue"], "Stack-based greedy": ["monotonic-stack"], "Sorting-based greedy": ["sorting"],
    "Two-pointer greedy": ["two-pointers"], "Greedy on graphs": ["graph"], "Bit greedy": ["bit-manipulation"], "Huffman": ["heap-priority-queue"],
    "Counting greedy": ["counting"],
    # Heap
    "Top-k selection": ["heap-priority-queue", "quickselect"], "Two heaps and the median": ["data-stream", "heap-priority-queue"],
    "Design problems with heaps": ["design", "heap-priority-queue"], "Heapify and heap sort": ["sorting", "heap-priority-queue"],
    "K-way merge": ["merge-sort", "heap-priority-queue"], "Scheduling with heaps": ["heap-priority-queue"], "Greedy with a heap": ["heap-priority-queue"],
    "Heaps in graph algorithms": ["shortest-path", "heap-priority-queue"], "Lazy deletion and indexed heaps": ["heap-priority-queue"],
    "Heap plus hash map": ["heap-priority-queue", "hash-table"], "Heaps on grids": ["matrix", "heap-priority-queue"],
    "Huffman coding and merge costs": ["heap-priority-queue"], "Order-statistic alternatives": ["quickselect", "ordered-set"],
    # Intervals
    "Line sweep": ["sweep-line"], "Skyline problem": ["sweep-line", "segment-tree"], "Range updates with difference arrays": ["prefix-sum"],
    "Calendar booking": ["design", "ordered-set"], "Meeting rooms": ["sweep-line"], "Interval tree and stabbing queries": ["segment-tree"],
    "Queries on intervals (offline sort + heap)": ["heap-priority-queue", "sorting"],
    # Linked list
    "Fast and slow pointers": ["two-pointers", "linked-list"], "Merging and sorting": ["merge-sort", "sorting"], "Random node": ["reservoir-sampling", "randomized"],
    "Design with linked lists": ["design", "doubly-linked-list"], "Reversal": ["linked-list"], "Dummy head and in-place surgery": ["linked-list"],
    "Intersection and comparison": ["linked-list", "two-pointers"], "Copy with a random pointer": ["hash-table", "linked-list"],
    # Math & geometry
    "Geometry": ["geometry"], "GCD, LCM and divisibility": ["number-theory"], "Probability and random": ["probability-and-statistics", "randomized"],
    "Combinatorics": ["combinatorics"], "Counting and number properties": ["number-theory", "counting"], "Matrix on grids": ["matrix"],
    "Simulation and sequences": ["simulation"], "Digit manipulation": ["math"], "Bit tricks (cross-reference)": ["bit-manipulation"],
    "Math plus greedy": ["greedy"], "Exponentiation and roots": ["math"],
    # Sliding window
    "Fixed-size window": ["sliding-window"], "Variable window, longest valid": ["sliding-window"], "Variable window, shortest valid": ["sliding-window"],
    "Counting windows (atMost(k) - atMost(k-1))": ["sliding-window", "counting"], "Monotonic-queue windows": ["monotonic-queue", "sliding-window"],
    "Ordered-set / heap windows": ["ordered-set", "heap-priority-queue"], "Negative numbers (when windows fail: prefix sums)": ["prefix-sum"],
    "Binary search on window size": ["binary-search", "sliding-window"], "Frequency (need / have) windows": ["sliding-window", "hash-table"],
    "Circular arrays": ["sliding-window"], "2-D windows": ["matrix", "prefix-sum"],
    # Stack
    "Monotonic stack": ["monotonic-stack"], "Monotonic queue (cross-reference: Sliding Window)": ["monotonic-queue"],
    "Stack and queue design": ["design", "queue"], "Matching and nesting": ["stack", "string"], "Expression evaluation": ["stack", "math"],
    "Parsing": ["stack", "string"], "Iterative DFS and tree traversal": ["stack", "binary-tree"], "Recursion to iteration": ["stack", "recursion"],
    "Sorting with stacks": ["stack", "sorting"], "Simulation with a stack": ["stack", "simulation"], "Stack and greedy": ["stack", "greedy"],
    "Stack and DP": ["stack", "dynamic-programming"], "Queues next to stacks (round simulation and streams)": ["queue", "data-stream"],
    # Trees
    "BST operations": ["binary-search-tree"], "Level-order family": ["breadth-first-search", "binary-tree"], "Traversals": ["depth-first-search", "binary-tree"],
    "Iterator design": ["iterator", "design"], "Lowest common ancestor": ["binary-tree"], "Construction": ["binary-tree", "divide-and-conquer"],
    "Subtree aggregation": ["binary-tree"], "Path problems": ["binary-tree"], "Tree comparison": ["binary-tree"], "Transformations": ["binary-tree"],
    "Views": ["binary-tree"], "Count and enumerate trees": ["binary-tree", "dynamic-programming"], "N-ary trees": ["tree"],
    # Tries
    "Basic trie": ["trie"], "Wildcards and approximate matching (DFS through the trie)": ["trie"], "Word search on a grid with a trie (pruning)": ["trie", "backtracking"],
    "XOR with a binary trie": ["trie", "bit-manipulation"], "Deleting from a trie and trie updates": ["trie"], "Compressed trie, radix tree and relatives": ["trie"],
    "Suffix structures (cross-reference to string algorithms)": ["suffix-array", "string-matching"], "Aho-Corasick multi-pattern matching": ["string-matching", "trie"],
    "Trie with DP (word break and its cousins)": ["trie", "dynamic-programming"], "Palindrome pairs and pairs of words": ["trie"],
    "Design problems": ["design", "trie"], "Trie versus hash set, sorting and hashing (trade-offs)": ["trie", "hash-table"],
    # Two pointers
    "Opposite-end pointers": ["two-pointers"], "Same-direction pointers (reader / writer, fast / slow)": ["two-pointers"], "String pointers": ["two-pointers", "string"],
    "Partition pointers": ["two-pointers"], "Pointers and greedy": ["two-pointers", "greedy"], "K-sum on sorted arrays": ["two-pointers", "sorting"],
}
# tags that name a whole topic rather than a technique: a group tagged only with these gets a link, not a problem list
GENERIC = set("array string hash-table math graph matrix greedy dynamic-programming binary-tree tree sorting simulation design two-pointers "
              "linked-list stack backtracking binary-search heap-priority-queue bit-manipulation sliding-window breadth-first-search "
              "depth-first-search recursion counting enumeration binary-search-tree queue".split())
GROUP_PROBLEMS = 8
STOP = set("with from that this into over when each using versus number numbers path paths sums problem problems based type types given "
           "with without where which then than also both only same more most less least many some such other another their there these "
           "those about after before between during while until still just like even much very make makes made take takes taken".split())


def norm(s):
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())


def fetch_index():
    def q(query, variables):
        out = subprocess.run(["curl", "-s", "-m", "40", "https://leetcode.com/graphql", "-H", "content-type: application/json", "-H", "referer: https://leetcode.com",
                              "-d", json.dumps({"query": query, "variables": variables})], capture_output=True, text=True).stdout
        return json.loads(out)
    Q = """query p($skip: Int, $limit: Int) { problemsetQuestionList: questionList(categorySlug: "", limit: $limit, skip: $skip, filters: {}) {
      total: totalNum questions: data { id: questionFrontendId title titleSlug difficulty isPaidOnly topicTags { slug } } } }"""
    out, skip, total = [], 0, None
    while total is None or skip < total:
        d = q(Q, {"skip": skip, "limit": 100})["data"]["problemsetQuestionList"]
        total = d["total"]
        out += d["questions"]
        skip += 100
    idx = [{"id": int(x["id"]) if str(x["id"]).isdigit() else 0, "title": x["title"], "slug": x["titleSlug"], "difficulty": x["difficulty"].lower(),
            "premium": x["isPaidOnly"], "tags": [t["slug"] for t in x["topicTags"]]} for x in out]
    INDEX.write_text(json.dumps(idx))
    r = q("query { questionTopicTags { edges { node { name slug } } } }", {})
    TAGS.write_text(json.dumps({e["node"]["slug"]: e["node"]["name"] for e in r["data"]["questionTopicTags"]["edges"]}))


def split_top(text, sep=";"):
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def name_note(item):
    item = item.strip().rstrip(".")
    if item.endswith(")"):
        depth = 0
        for i in range(len(item) - 1, -1, -1):
            if item[i] == ")":
                depth += 1
            elif item[i] == "(":
                depth -= 1
                if depth == 0 and i > 0:
                    return item[:i].strip(), item[i + 1:-1].strip()
    return item, ""


def candidates(item):
    name, note = name_note(item)
    cands = [name]
    for part in re.split(r",| and | or |;|/", note):
        p = part.strip().strip(".").strip()
        low = p.lower()
        if not p or low.startswith(("see ", "e.g")) or len(p.split()) > 7:
            continue
        cands.append(p)
    return cands


def tokens(text):
    return {w for w in norm(text).split() if len(w) >= 4 and w not in STOP}


def q(s):
    return json.dumps(s, ensure_ascii=False)


def group_tag_set(group, lc_tags):
    for key, ts in GROUP_TAGS.items():
        if key.lower() == group.lower() or key.lower().startswith(group.lower()) and len(group) > 12:
            return {t for t in ts if t in lc_tags}
    return set()


def fuzzy(cands, group_tags, lc, lc_tags_all):
    """Problems whose title is (almost) one of the example names in the item and that carry one of the group's topic tags.
    An example name matches a title when every informative word of the shorter one is in the longer one (at least two words)."""
    out = {}
    for c in cands:
        ct = tokens(c)
        if len(ct) < 3:
            continue
        for p in lc:
            if group_tags and not (group_tags & set(p["tags"])):
                continue
            pt = tokens(p["title"])
            if len(pt) < 2:
                continue
            small, big = (ct, pt) if len(ct) <= len(pt) else (pt, ct)
            if len(small) >= 3 and small <= big and len(small) / len(big) >= 0.6:
                out[p["slug"]] = p
    return out


PHRASE_STOP = {"sum", "pow", "trap", "sort", "search", "merge", "game", "stack", "queue", "tree", "graph", "heap", "string", "array", "list",
               "count", "find", "range", "design", "maximum", "minimum", "median", "pairs", "subsets", "closest", "reverse", "rotate", "simplify path"}


def phrases(item, by_len, group_tags):
    """Problems whose whole title is, word for word, where the item starts or inside its examples (the part in parentheses).
    A title merely occurring in the middle of the description ("LIS with a maximum gap" and Maximum Gap) is not enough."""
    name, note = name_note(item)
    head, examples = " " + norm(name) + " ", " " + norm(note) + " "
    out = {}
    for n, plist in by_len:
        if head.startswith(f" {n} ") or f" {n} " in examples:
            for p in plist:
                if group_tags and not (group_tags & set(p["tags"])):
                    continue
                out[p["slug"]] = p
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--fetch" in sys.argv or not INDEX.exists():
        fetch_index()
    dry = "--dry-run" in sys.argv
    # no SQL, shell or concurrency problems, and none without a topic tag (the pandas ones)
    lc = [p for p in json.loads(INDEX.read_text()) if p["tags"] and not {"database", "shell", "concurrency"} & set(p["tags"])]
    lc_tags = json.loads(TAGS.read_text())
    lc_by_slug = {p["slug"]: p for p in lc}
    by_title = {}
    for p in lc:
        by_title.setdefault(norm(p["title"]), []).append(p)
    # titles worth looking for inside a longer text: at least two words, or a long single word, and not a generic one
    by_len = sorted(((n, ps) for n, ps in by_title.items()
                     if n not in PHRASE_STOP and (len(n.split()) >= 2 or len(n) >= 8) and len(n) >= 6), key=lambda x: -len(x[0]))
    # curated technique keywords -> problem slugs; a slug that LeetCode's index does not have is dropped and reported
    curated = {}
    for kw, slugs in json.loads((ROOT / "tools/neetcode/item_examples.json").read_text()).items():
        if kw.startswith("_"):
            continue
        ok = [sl for sl in slugs if sl in {x["slug"] for x in lc}]
        for sl in slugs:
            if sl not in ok:
                print(f"item_examples.json: {kw!r}: {sl} is not in LeetCode's index (or is a database problem)", file=sys.stderr)
        curated[norm(kw)] = ok
    curated_groups = {k: v for k, v in json.loads((ROOT / "tools/neetcode/group_examples.json").read_text()).items() if not k.startswith("_")}
    for key, slugs in curated_groups.items():
        for sl in slugs:
            if sl not in lc_by_slug:
                print(f"group_examples.json: {key!r}: {sl} is not in LeetCode's index (or is not a tagged problem)", file=sys.stderr)
    lists = json.loads((ROOT / "content/dsa/problems.json").read_text())
    list_by_slug = {p["slug"]: p for p in lists["problems"]}
    technique_names = {t["id"]: t["name"] for t in lists["techniques"]}
    only = set(args)
    report = []
    for doc_key, patterns in DOCS_TO_PATTERNS.items():
        if only and not (only & {doc_key, *patterns}):
            continue
        text = (DOCS / f"DSA_{doc_key}_PATTERNS.md").read_text()
        first = re.search(r"^1\. \*\*", text, re.M)
        end = re.search(r"^## ", text[first.start():], re.M) if first else None
        body = text[first.start(): first.start() + end.start()] if first and end else text
        groups = [(m.group(2), m.group(3)) for m in re.finditer(r"^(\d+)\. \*\*(.+?)\.\*\* (.+)$", body, re.M)]
        files = {}
        for pat in patterns:
            slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", pat.lower())).strip("-")
            files[pat] = LESSONS / f"{slug}.toml"
        docs_toml = {pat: tomllib.loads(f.read_text()) for pat, f in files.items()}
        declared = {pat: d.get("groups", []) for pat, d in docs_toml.items()}
        # which pattern a group belongs to: the one that already declares it, else the first
        owner = {}
        for pat in patterns:
            for g in declared[pat]:
                owner.setdefault(g, pat)
        for g, _ in groups:
            owner.setdefault(g, patterns[0])
        # the text of every lesson of the document's patterns, for related-lesson pointers
        lesson_text = {}
        for pat in patterns:
            for t in docs_toml[pat]["technique"]:
                lesson_text[t["id"]] = tokens(" ".join([technique_names.get(t["id"], ""), *t["signals"], *t["pitfalls"], t["template"][:400]]))
            for e in docs_toml[pat].get("extra", []):
                lesson_text[e["id"]] = tokens(" ".join([e["name"], *e["signals"], *e["pitfalls"]]))
        names = {**technique_names, **{e["id"]: e["name"] for d in docs_toml.values() for e in d.get("extra", [])}}
        votes = {}  # technique id -> {group: n}
        listed = {pat: [] for pat in patterns}
        stats = {"items": 0, "covered": 0, "listed": 0, "with_problems": 0}
        for g, body in groups:
            for item in split_top(body):
                name, note = name_note(item)
                if not name or len(name) < 3 or name.lower().startswith("define the state"):
                    continue
                stats["items"] += 1
                found = {}
                cands = candidates(item)
                for c in cands:
                    for p in by_title.get(norm(c), []):
                        found[p["slug"]] = p
                if not found:
                    found.update(phrases(item, by_len, group_tag_set(g, lc_tags) - GENERIC))
                if not found:
                    found.update(fuzzy(cands, group_tag_set(g, lc_tags), lc, lc_tags))
                # curated technique keywords: a problem must share a LeetCode tag with the group (so a keyword cannot cross topics)
                gtags = group_tag_set(g, lc_tags)
                if gtags:
                    nm = " " + norm(name) + " "
                    for kw, slugs in curated.items():
                        if f" {kw} " in nm:
                            for sl in slugs:
                                pr = lc_by_slug[sl]
                                if gtags & set(pr["tags"]):
                                    found[sl] = pr
                in_lists = [list_by_slug[s] for s in found if s in list_by_slug]
                if in_lists:
                    stats["covered"] += 1
                    for p in in_lists:
                        votes.setdefault(p["technique"], {})
                        votes[p["technique"]][g] = votes[p["technique"]].get(g, 0) + 1
                    continue
                probs = sorted(found.values(), key=lambda p: (p["premium"], p["id"]))[:3]
                # an existing lesson that mentions its key words
                kw = tokens(name)
                related, best = None, 0.0
                for tid, toks in lesson_text.items():
                    if kw and toks:
                        score = len(kw & toks) / len(kw)
                        if score > best and len(kw & toks) >= 1 and score >= 0.5:
                            related, best = tid, score
                shown = name[0].upper() + name[1:]
                n = ""
                if related:
                    n = f"Related lesson: {names.get(related, related.split(':')[-1])}"
                elif note and not note.lower().startswith("see "):
                    n = "e.g. " + note if len(note) < 140 else ""
                listed[owner[g]].append({"name": shown, "group": g, "note": n, "problems": probs})
                stats["listed"] += 1
                stats["with_problems"] += bool(probs)
        # more problems per group: carry one of the group's specific tags, not in the lists, not already attached
        attached = {p["slug"] for pat in patterns for it in listed[pat] for p in it["problems"]}
        gprobs = {}
        used = set()  # a problem is shown under one group of a page only
        for g, _ in groups:
            take = []
            # the curated ones for this section first (checked against the index), then the section's topic tags
            keys = sorted((k for k in curated_groups if g.lower().startswith(k.lower())), key=len, reverse=True)
            for sl in (curated_groups[keys[0]] if keys else []):
                pr = lc_by_slug.get(sl)
                if pr and sl not in list_by_slug and sl not in attached and sl not in used and pr not in take:
                    take.append(pr)
            spec = group_tag_set(g, lc_tags) - GENERIC
            if spec and len(take) < GROUP_PROBLEMS:
                pool = [p for p in lc if spec & set(p["tags"]) and p["slug"] not in list_by_slug and p["slug"] not in attached
                        and p["slug"] not in used and p not in take]
                pool.sort(key=lambda p: (-len(spec & set(p["tags"])), p["premium"], p["id"]))
                take += pool[:GROUP_PROBLEMS - len(take)]
            take = take[:GROUP_PROBLEMS]
            if take:
                gprobs[g] = take
                used |= {p["slug"] for p in take}
        stats["group_problems"] = sum(len(v) for v in gprobs.values())
        # write the files
        for pat, path in files.items():
            s = path.read_text()
            d = docs_toml[pat]
            glist = declared[pat] or [g for g, _ in groups if owner[g] == pat]
            if not declared[pat]:
                m = re.search(r"^intro = .*\n", s, re.M)
                s = s[:m.end()] + "groups = [" + ", ".join(q(g) for g in glist) + "]\n" + s[m.end():]
            # a technique's group: its own if set, else the group that most of its matched items sit in
            def put_group(m2):
                tid = m2.group(1)
                if re.match(r"group = ", s[m2.end():m2.end() + 8]):
                    return m2.group(0)
                v = votes.get(tid)
                if not v:
                    # the group whose LeetCode tags its problems carry most, then the group whose title shares words with its name
                    tcount = {}
                    for pr in lists["problems"]:
                        if pr["technique"] == tid and pr["slug"] in lc_by_slug:
                            for tg in lc_by_slug[pr["slug"]]["tags"]:
                                tcount[tg] = tcount.get(tg, 0) + 1
                    scored = []
                    for gi, g in enumerate(glist):
                        gt = group_tag_set(g, lc_tags)
                        spec = gt - GENERIC
                        score = sum(tcount.get(t, 0) for t in spec) * 3 + sum(tcount.get(t, 0) for t in gt & GENERIC)
                        words = len(tokens(technique_names.get(tid, "")) & tokens(g))
                        scored.append((score + words * 4, -gi, g))
                    top = max(scored) if scored else None
                    if top and top[0] > 0:
                        return m2.group(0) + f"group = {q(top[2])}\n"
                    return m2.group(0)
                best = max(v.items(), key=lambda kv: (kv[1], -glist.index(kv[0]) if kv[0] in glist else -999))[0]
                return m2.group(0) + f"group = {q(best)}\n" if best in glist else m2.group(0)
            s = re.sub(r'\[\[technique\]\]\nid = "([^"]+)"\n', put_group, s)
            # group tags
            tags = {}
            for g in glist:
                ts = sorted(group_tag_set(g, lc_tags), key=lambda t: (t in GENERIC, t))
                if ts:
                    tags[g] = ts
            s = re.sub(r"\n\[group_tags\]\n(?:(?!\[\[).*\n)*", "\n", s)
            tag_block = "\n[group_tags]\n" + "".join(f"{q(g)} = [{', '.join(q(t) for t in ts)}]\n" for g, ts in tags.items()) + "\n" if tags else ""
            s = s.replace("[[technique]]", tag_block + "[[technique]]", 1) if tag_block else s
            # listed: replace all
            s = re.sub(r"\n\[\[listed\]\]\n(?:(?!\n\[\[)(?:.*\n?))*", "", s)
            s = re.sub(r"\n\[\[group_problem\]\]\n(?:(?!\n\[\[)(?:.*\n?))*", "", s).rstrip("\n") + "\n"
            for g in glist:
                for p in gprobs.get(g, []):
                    s += (f"\n[[group_problem]]\ngroup = {q(g)}\nslug = {q(p['slug'])}\ntitle = {q(p['title'])}\nnumber = {p['id']}\n"
                          f"difficulty = {q(p['difficulty'])}\npremium = {str(p['premium']).lower()}\n")
            for it in listed[pat]:
                s += f"\n[[listed]]\nname = {q(it['name'])}\ngroup = {q(it['group'])}\n"
                if it["note"]:
                    s += f"note = {q(it['note'])}\n"
                if it["problems"]:
                    s += "problems = [\n" + "".join(
                        f"    {{ slug = {q(p['slug'])}, title = {q(p['title'])}, number = {p['id']}, difficulty = {q(p['difficulty'])}, premium = {str(p['premium']).lower()} }},\n"
                        for p in it["problems"]) + "]\n"
            if not dry:
                path.write_text(s)
        report.append((doc_key, stats))
    for k, st in report:
        print(f"{k:18} items={st['items']:4} covered_by_lists={st['covered']:4} listed={st['listed']:4} with_problems={st['with_problems']:4} group_problems={st['group_problems']:4}")


main()
