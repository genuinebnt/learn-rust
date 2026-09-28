#!/usr/bin/env python3
"""Fails when a change would lose someone's progress. CI runs it against the previous commit (or a PR's base):

    python3 tools/check-progress-safety.py <base-rev>

1. Every problem id at <base-rev> must still exist, or be listed in some problem's `renamed_from`. Progress is stored
   by id (`<track code>-<slug>`), so a renamed, moved or deleted problem would otherwise vanish from every dashboard.
2. Migrations are append-only: editing or deleting an applied one makes the API refuse to start.

The deploy runs the stronger check too (`anneal-api preflight` against the live database), so this is the early
warning, not the only one.
"""
import pathlib
import subprocess
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def ids_at(rev):
    """Problem ids at a revision, from the paths: content/tracks/<code>-<name>/problems/<slug>/problem.toml."""
    ids = set()
    for path in git("ls-tree", "-r", "--name-only", rev, "--", "content/tracks").splitlines():
        parts = path.split("/")
        if len(parts) == 6 and parts[3] == "problems" and parts[5] == "problem.toml":
            ids.add(f"{parts[2].split('-')[0]}-{parts[4]}")
    return ids


def current():
    ids, renamed = set(), {}
    for track in sorted((ROOT / "content/tracks").iterdir()):
        if not (track / "track.toml").is_file():
            continue
        code = tomllib.loads((track / "track.toml").read_text())["code"].lower()
        if track.name.split("-")[0] != code:
            sys.exit(f"{track.name}: directory must start with the track code ({code}-...), ids are derived from it")
        for problem in sorted((track / "problems").glob("*/problem.toml")):
            meta = tomllib.loads(problem.read_text())
            pid = f"{code}-{meta['slug']}"
            ids.add(pid)
            for old in meta.get("renamed_from", []):
                renamed[old] = pid
    return ids, renamed


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = sys.argv[1]
    problems = []

    ids, renamed = current()
    for gone in sorted(ids_at(base) - ids - renamed.keys()):
        problems.append(
            f"problem {gone} disappeared. If it was renamed or moved, add renamed_from = [\"{gone}\"] to its "
            "problem.toml; progress stored under the old id then moves to it. Deleting a problem isn't supported."
        )

    for line in git("diff", "--name-status", base, "HEAD", "--", "crates/api/migrations").splitlines():
        status, *paths = line.split("\t")
        if not status.startswith("A"):
            problems.append(f"migration {paths[0]} was {'edited' if status == 'M' else 'removed or renamed'}; "
                            "migrations are append-only, add a new one instead")

    for p in problems:
        print(f"::error::{p}")
    if problems:
        sys.exit(1)
    print(f"progress safety: ok ({len(ids)} problems, {len(renamed)} renames, compared with {base[:12]})")


main()
