#!/usr/bin/env python3
"""Merge a course's fine-grained stages into substantial ones, following a plan.

Why: a stage should be a real piece of work (tens of lines and a design decision), not a one-line change. The plan lists, per
module, which old stages become one new stage. This script
  * renumbers the stages (new ids are sequential per module),
  * rewrites every old id found in the reference sources, tests and stage text with one simultaneous substitution,
  * writes each merged stage.toml (tests = the union, difficulty = the hardest) and stage.md (one "Part" per old stage).
Run from the repo root: tools/course_merge.py courses/bustub tools/course_merge_plan.json
"""
import json, os, re, shutil, sys

DIFF = ["very-easy", "easy", "medium", "hard"]


def slug(t):
    s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return "-".join(s.split("-")[:6])


def demote(md):
    out, fence = [], False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        out.append("#" + line if (not fence and line.startswith("#")) else line)
    return "\n".join(out)


def main(root, plan_path):
    plan = json.load(open(plan_path))
    old = {}  # old id -> (dir, toml fields, md)
    order = {}  # module code -> [old ids in order]
    for mdir in sorted(os.listdir(f"{root}/modules")):
        mt = open(f"{root}/modules/{mdir}/module.toml").read()
        code = re.search(r'code = "(\w+)"', mt).group(1)
        order[code] = []
        for sd in sorted(os.listdir(f"{root}/modules/{mdir}/stages")):
            p = f"{root}/modules/{mdir}/stages/{sd}"
            t = open(f"{p}/stage.toml").read()
            sid = re.search(r'^id = "([^"]+)"', t, re.M).group(1)
            old[sid] = dict(
                dir=p, mdir=mdir, code=code,
                title=re.search(r'^title = "(.*)"$', t, re.M).group(1),
                kind=re.search(r'^kind = "(\w+)"', t, re.M).group(1),
                diff=re.search(r'^difficulty = "([\w-]+)"', t, re.M).group(1),
                tests=re.findall(r'"([^"]+)"', re.search(r"^tests = \[(.*?)\]", t, re.M | re.S).group(1)),
                retest="retest = true" in t,
                md=open(f"{p}/stage.md").read(),
            )
            order[code].append(sid)
    mapping, groups = {}, []
    for code, plans in plan.items():
        n = 0
        covered = []
        for g in plans:
            n += 1
            new = f"{code}-{n:02d}"
            ids = [f"{code}-{i:02d}" for i in range(g["from"], g["to"] + 1)] if "from" in g else g["ids"]
            for i in ids:
                assert i in old, f"{i} not found"
                mapping[i] = new
            covered += ids
            groups.append((code, new, ids, g.get("title")))
        assert covered == order[code], f"{code}: plan does not cover the stages exactly once and in order: {covered} vs {order[code]}"
    pat = re.compile(r"\b(\d[a-g])-(\d\d)\b")
    sub = lambda text: pat.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)
    # 1. relabel everything that mentions a stage id (reference sources and tests)
    ref = f"{root}/reference"
    for dp, _, fs in os.walk(ref):
        if "/target" in dp or "/.git" in dp:
            continue
        for f in fs:
            if f.endswith((".rs", ".toml", ".md")):
                p = os.path.join(dp, f)
                s = open(p).read()
                n = sub(s)
                if n != s:
                    open(p, "w").write(n)
    # 2. write the merged stages
    for code, new, ids, title in groups:
        first = old[ids[0]]
        if len(ids) == 1:
            kind, diff, tests, retest = first["kind"], first["diff"], first["tests"], first["retest"]
            body = sub(first["md"])
            ttl = title or first["title"]
        else:
            kind = "build"
            diff = DIFF[max(DIFF.index(old[i]["diff"]) for i in ids)]
            tests = [t for i in ids for t in old[i]["tests"]]
            retest = any(old[i]["retest"] for i in ids)
            ttl = title
            parts = [f"This stage has {len(ids)} parts. Work through them in order; they build on each other, and every test in the stage has to pass.\n"]
            for k, i in enumerate(ids, 1):
                parts.append(f"## Part {k} · {old[i]['title']}\n\n{demote(sub(old[i]['md'])).strip()}\n")
            body = "\n".join(parts)
        mdir = first["mdir"]
        nd = f"{root}/modules/{mdir}/stages/{new.split('-')[1]}-{slug(ttl)}"
        os.makedirs(nd + ".new", exist_ok=True)
        tl = ", ".join(f'"{t}"' for t in tests)
        open(f"{nd}.new/stage.toml", "w").write(
            f'id = "{new}"\ntitle = "{ttl}"\nkind = "{kind}"\ndifficulty = "{diff}"\ntests = [{tl}]\n' + ("retest = true\n" if retest else "")
        )
        open(f"{nd}.new/stage.md", "w").write(body.rstrip() + "\n")
    # 3. swap the old stage directories for the new ones
    for sid, o in old.items():
        shutil.rmtree(o["dir"], ignore_errors=True)
    for dp, ds, _ in list(os.walk(f"{root}/modules")):
        for d in ds:
            if d.endswith(".new"):
                os.rename(os.path.join(dp, d), os.path.join(dp, d[:-4]))
    print(f"{len(old)} stages -> {len(groups)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
