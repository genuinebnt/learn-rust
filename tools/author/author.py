"""Writes anneal problem folders from compact Python specs.

The folders under content/tracks are the source of truth; this only saves typing.
"""
import json
import os
import re
import shutil
import textwrap

# content/tracks in this repo; ANNEAL_CONTENT_ROOT overrides it (e.g. to regenerate into a scratch copy and diff).
ROOT = os.environ.get("ANNEAL_CONTENT_ROOT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "content", "tracks")


def q(s: str) -> str:
    # JSON string syntax is valid TOML basic-string syntax for everything we write.
    return json.dumps(s, ensure_ascii=False)


def arr(xs) -> str:
    return "[" + ", ".join(q(x) for x in xs) + "]"


def dedent(s: str) -> str:
    return textwrap.dedent(s).strip("\n") + "\n"


def T(name, input_desc, call, expected, setup=""):
    """One check!-based test."""
    return ("case", name, input_desc, call, expected, setup)


def render_tests(items, use="use solution::*;"):
    out = [use, ""] if use else []
    for it in items:
        if isinstance(it, str):
            out.append(dedent(it))
            continue
        _, name, input_desc, call, expected, setup = it
        # A test named like a function it calls would shadow the glob-imported function.
        free_call = re.compile(rf"(?<![\w.:]){re.escape(name)}\(")
        assert not free_call.search(call) and not free_call.search(setup), f"test {name} shadows a function it calls"
        body = ""
        if setup:
            body += textwrap.indent(dedent(setup), "    ")
        hashes = "#"
        while '"' + hashes in input_desc:
            hashes += "#"
        body += f'    check!(r{hashes}"{input_desc}"{hashes}, {call}, {expected});\n'
        out.append(f"#[test]\nfn {name}() {{\n{body}}}\n")
    return "\n".join(out).rstrip("\n") + "\n"


def write_track(slug, code, name, section, tier, order, summary, stages, problems, keep=()):
    """Writes track.toml and every problem. `keep` lists slugs already written by hand
    (their folder is left alone but their position still counts toward `order`)."""
    tdir = os.path.join(ROOT, slug)
    os.makedirs(os.path.join(tdir, "problems"), exist_ok=True)
    lines = [f"code = {q(code)}", f"name = {q(name)}", f"section = {q(section)}", f"tier = {q(tier)}", f"order = {order}", f"summary = {q(summary)}", ""]
    for s_slug, s_name, band in stages:
        lines += ["[[stages]]", f"slug = {q(s_slug)}", f"name = {q(s_name)}", f"band = {q(band)}", ""]
    with open(os.path.join(tdir, "track.toml"), "w") as f:
        f.write("\n".join(lines))
    wanted = set()
    for i, p in enumerate(problems, 1):
        wanted.add(p["slug"])
        if p["slug"] in keep:
            continue
        write_problem(tdir, p, i)
    # Drop old folders that are no longer in the track (e.g. renamed drafts).
    for d in os.listdir(os.path.join(tdir, "problems")):
        if d not in wanted and d not in keep:
            shutil.rmtree(os.path.join(tdir, "problems", d))
    return len(problems)


def write_problem(tdir, p, order):
    d = os.path.join(tdir, "problems", p["slug"])
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "tests"))
    ready = "solution" in p
    t = [
        f"slug = {q(p['slug'])}",
        f"title = {q(p['title'])}",
        f"mode = {q(p.get('mode', 'write'))}",
        f"level = {q(p['level'])}",
        f"stage = {q(p['stage'])}",
        f"order = {order}",
        f"status = {q('ready' if ready else 'draft')}",
        f"tags = {arr(p.get('tags', []))}",
    ]
    if p.get("teaches"):
        t.append("teaches = [\n" + "".join(f"  {q(x)},\n" for x in p["teaches"]) + "]")
    if p.get("constraints"):
        t.append(f"constraints = {arr(p['constraints'])}")
    if p.get("follow_up"):
        t.append(f"follow_up = {q(p['follow_up'])}")
    if p.get("related"):
        t.append(f"related = {arr(p['related'])}")
    if p.get("source"):
        t.append(f"source = {q(p['source'])}")
    if p.get("crates"):
        t.append(f"crates = {arr(p['crates'])}")
    for inp, out in p.get("examples", []):
        t += ["", "[[examples]]", f"input = {q(inp)}", f"output = {q(out)}"]
    for kind, text in p.get("hints", []):
        t += ["", "[[hints]]", f"kind = {q(kind)}", f"text = {q(text)}"]
    if p.get("notes"):
        expl, time, space = p["notes"]
        t += ["", "[solution]", f"explanation = {q(expl)}", f"time = {q(time)}", f"space = {q(space)}"]
    if p.get("rules"):
        r = p["rules"]
        t += ["", "[rules]"]
        if r.get("methods"):
            t.append(f"forbid_methods = {arr(r['methods'])}")
        if r.get("types"):
            t.append(f"forbid_types = {arr(r['types'])}")
        if r.get("unsafe"):
            t.append("forbid_unsafe = true")
        if r.get("lines") is not None:
            t.append(f"max_changed_lines = {r['lines']}")
    with open(os.path.join(d, "problem.toml"), "w") as f:
        f.write("\n".join(t) + "\n")
    if not ready:
        return
    with open(os.path.join(d, "statement.md"), "w") as f:
        f.write(dedent(p["statement"]))
    with open(os.path.join(d, "starter.rs"), "w") as f:
        f.write(dedent(p["starter"]))
    with open(os.path.join(d, "solution.rs"), "w") as f:
        f.write(dedent(p["solution"]))
    use = p.get("use", "use solution::*;")
    with open(os.path.join(d, "tests", "visible.rs"), "w") as f:
        f.write(render_tests(p["visible"], use))
    with open(os.path.join(d, "tests", "hidden.rs"), "w") as f:
        f.write(render_tests(p["hidden"], use))


def draft(slug, title, mode, level, stage, tags):
    return dict(slug=slug, title=title, mode=mode, level=level, stage=stage, tags=tags)


def prob(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches,
         mode="write", **extra):
    """Positional shorthand for a problem dict. Rules are dropped on write problems (the validator rejects them)."""
    d = dict(slug=slug, title=title, mode=mode, level=level, stage=stage, tags=tags, statement=statement, starter=starter,
             solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up, teaches=teaches)
    d.update({k: v for k, v in extra.items() if v is not None})
    if mode == "write":
        d.pop("rules", None)
    return d
