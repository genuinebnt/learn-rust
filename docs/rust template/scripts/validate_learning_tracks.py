"""Structural + compilation validator for the algorithm learning tracks.

Defines the shared HTML/ID/progress-manifest contract that the five
learning-track pages must satisfy, and a CLI entry point (`main`) that runs
every check against the real repository.

    part-learn-linked-lists.html   24 exercises, 12 fully worked
    part-learn-trees.html          50 exercises, 24 fully worked
    part-learn-tries.html          20 exercises, 10 fully worked
    part-learn-graphs.html         70 exercises, 30 fully worked
    part-learn-dp.html             80 exercises, 32 fully worked

Contract summary (see README-style notes above each check function below):

- Every exercise is a `<div class="card" id="{prefix}-{NN}" data-tier="core|
  reinforcement">`, `NN` a 2-digit, 1-based, gap-free sequence per track.
- Each card carries a `Learning NN` chip (replaces LeetCode-number chips —
  `LC <number>` chips are forbidden anywhere in these five files) and an
  `sb-check` span whose `data-id` equals the card's own id.
- Each card has six required metadata blocks: Prerequisites, New idea,
  Hint ladder, Complexity, Rust angle, Unlocks next (`<strong>Field:</strong>`
  style, matching the existing Blind 75 card convention).
- `core` (fully-worked) cards need a `<details>` "Solution" block containing
  a `<pre>` with a complete, compilable, asserting Rust program.
  `reinforcement` cards need a "Solution sketch" instead.
- Each track page is split into five `<div class="section"
  id="{prefix}-stage-{foundation|easy|medium|hard|mastery}">` stages, in
  that order, each carrying a "Read before" block plus a "Review after"
  and/or "Further reading" block.
- All internal `href="#id"` anchors must resolve within the same file.
- Every learn-* id must be globally unique across the whole site.
- `index.html` must define a JS array (`LEARNING_TRACK_IDS`) whose contents
  exactly match the union of learn-* ids across the five track files, so the
  global progress total stays stable even when a track page isn't loaded.

Run tests with:
    python3 -m unittest test_validate_learning_tracks -v
(from this directory).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rust_highlight import strip_html  # noqa: E402  (reuse existing HTML stripper)

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"

TIER_CORE = "core"
TIER_REINFORCEMENT = "reinforcement"
VALID_TIERS = (TIER_CORE, TIER_REINFORCEMENT)

STAGES: tuple[str, ...] = ("Foundation", "Easy", "Medium", "Hard", "Mastery")

REQUIRED_FIELDS: tuple[str, ...] = (
    "Prerequisites",
    "New idea",
    "Hint ladder",
    "Complexity",
    "Rust angle",
    "Unlocks next",
)

MANIFEST_VAR = "LEARNING_TRACK_IDS"


@dataclass(frozen=True)
class TrackSpec:
    key: str
    prefix: str          # e.g. "learn-tree"
    filename: str        # e.g. "part-learn-trees.html"
    total: int
    worked: int


TRACKS: tuple[TrackSpec, ...] = (
    TrackSpec("linked-lists", "learn-list", "part-learn-linked-lists.html", 24, 12),
    TrackSpec("trees", "learn-tree", "part-learn-trees.html", 50, 24),
    TrackSpec("tries", "learn-trie", "part-learn-tries.html", 20, 10),
    TrackSpec("graphs", "learn-graph", "part-learn-graphs.html", 70, 30),
    TrackSpec("dp", "learn-dp", "part-learn-dp.html", 80, 32),
)

TOTAL_EXERCISES = sum(t.total for t in TRACKS)  # 244
TOTAL_WORKED = sum(t.worked for t in TRACKS)    # 108


# ── Card model ────────────────────────────────────────────────────────────

@dataclass
class Card:
    id: str
    seq: int
    tier: str
    body: str            # raw HTML from just after the opening <div> to the next card/section
    label: str | None     # e.g. "Learning 07", if found


_CARD_OPEN_RE = re.compile(
    r'<div class="card"\s+id="(?P<id>[\w-]+)"(?:\s+data-tier="(?P<tier>[\w-]+)")?[^>]*>'
)
_SECTION_OPEN_RE = re.compile(r'<div class="section"\s+id="[\w-]+">')
_LABEL_RE = re.compile(r"Learning\s+(\d{2,})")
_SEQ_SUFFIX_RE = re.compile(r"-(\d+)$")


def parse_cards(html: str) -> list[Card]:
    """Extract every `<div class="card" id="...">` block in document order.

    A card's body runs until the next card or section opening tag (or end of
    file), matching the boundary convention already used by
    `apply_tests.py`'s section/card splitting.
    """
    card_opens = list(_CARD_OPEN_RE.finditer(html))
    section_opens = list(_SECTION_OPEN_RE.finditer(html))
    boundaries = sorted(m.start() for m in card_opens + section_opens)

    cards: list[Card] = []
    for m in card_opens:
        start = m.end()
        end = next((b for b in boundaries if b > m.start()), len(html))
        body = html[start:end]
        cid = m.group("id")
        seq_m = _SEQ_SUFFIX_RE.search(cid)
        seq = int(seq_m.group(1)) if seq_m else -1
        label_m = _LABEL_RE.search(body)
        cards.append(
            Card(
                id=cid,
                seq=seq,
                tier=m.group("tier") or "",
                body=body,
                label=label_m.group(0) if label_m else None,
            )
        )
    return cards


# ── Label / ID ordering ───────────────────────────────────────────────────

def check_labels_ordered(cards: list[Card], total: int) -> list[str]:
    """`Learning NN` labels (and id suffixes) must be 01..total, gap-free, in
    document order — this is what replaces LeetCode numbering as the stable,
    human-readable position marker."""
    issues: list[str] = []
    for i, card in enumerate(cards, start=1):
        expected_label = f"Learning {i:02d}"
        if card.label != expected_label:
            issues.append(
                f"{card.id}: expected label '{expected_label}' at position {i}, found {card.label!r}"
            )
        if card.seq != i:
            issues.append(f"{card.id}: expected id suffix {i:02d} at position {i}, found {card.seq}")
    if len(cards) != total:
        issues.append(f"expected {total} labelled cards, found {len(cards)}")
    return issues


# ── Required metadata fields ──────────────────────────────────────────────

def _field_pattern(field_name: str) -> re.Pattern[str]:
    escaped = re.escape(field_name)
    return re.compile(rf"<strong>\s*{escaped}\s*:?\s*</strong>\s*:?", re.IGNORECASE)


_FIELD_PATTERNS = {f: _field_pattern(f) for f in REQUIRED_FIELDS}


def check_required_fields(card: Card) -> list[str]:
    issues = []
    for f in REQUIRED_FIELDS:
        if not _FIELD_PATTERNS[f].search(card.body):
            issues.append(f"{card.id}: missing required field '{f}'")
    return issues


# ── No LeetCode-number chips ───────────────────────────────────────────────

_LC_CHIP_RE = re.compile(r">\s*LC\s+\d+\s*<")


def check_no_lc_chips(html: str) -> list[str]:
    matches = _LC_CHIP_RE.findall(html)
    if matches:
        return [f"found {len(matches)} 'LC <number>' chip(s); learning tracks use 'Learning NN' labels instead"]
    return []


# ── Stage sections ─────────────────────────────────────────────────────────

def _stage_id(prefix: str, stage: str) -> str:
    return f"{prefix}-stage-{stage.lower()}"


def find_stage_positions(html: str, prefix: str) -> dict[str, int]:
    """Return {stage_name: start_offset} for stages present in `html`."""
    positions: dict[str, int] = {}
    for stage in STAGES:
        m = re.search(rf'<div class="section" id="{re.escape(_stage_id(prefix, stage))}">', html)
        if m:
            positions[stage] = m.start()
    return positions


def check_stages(html: str, prefix: str) -> list[str]:
    issues: list[str] = []
    positions = find_stage_positions(html, prefix)

    missing = [s for s in STAGES if s not in positions]
    for s in missing:
        issues.append(f"missing stage section '{_stage_id(prefix, s)}' ({s})")

    present_in_order = [s for s in STAGES if s in positions]
    offsets = [positions[s] for s in present_in_order]
    if offsets != sorted(offsets):
        issues.append(
            "stage sections are out of order: expected "
            f"{', '.join(STAGES)} but found them at offsets {positions}"
        )

    for stage, pos in positions.items():
        title_window = html[pos : pos + 400]
        title_m = re.search(r'<div class="sh-title">([^<]*)</div>', title_window)
        if not title_m or stage.lower() not in title_m.group(1).strip().lower():
            issues.append(f"stage '{_stage_id(prefix, stage)}' missing/mismatched sh-title '{stage}'")

    return issues


def _stage_slices(html: str, prefix: str) -> dict[str, str]:
    positions = find_stage_positions(html, prefix)
    ordered = sorted(positions.items(), key=lambda kv: kv[1])
    slices: dict[str, str] = {}
    for i, (stage, start) in enumerate(ordered):
        end = ordered[i + 1][1] if i + 1 < len(ordered) else len(html)
        slices[stage] = html[start:end]
    return slices


# ── Reading blocks ─────────────────────────────────────────────────────────

_READ_BEFORE_RE = _field_pattern("Read before")
_REVIEW_AFTER_RE = _field_pattern("Review after")
_FURTHER_READING_RE = _field_pattern("Further reading")


def check_reading_blocks(html: str, prefix: str) -> list[str]:
    """Every stage needs a 'Read before' block, plus 'Review after' and/or
    'Further reading' — stage-level citations instead of repeating them on
    every exercise (per the plan's reading-references contract)."""
    issues: list[str] = []
    for stage, chunk in _stage_slices(html, prefix).items():
        if not _READ_BEFORE_RE.search(chunk):
            issues.append(f"stage '{_stage_id(prefix, stage)}': missing 'Read before' block")
        if not (_REVIEW_AFTER_RE.search(chunk) or _FURTHER_READING_RE.search(chunk)):
            issues.append(
                f"stage '{_stage_id(prefix, stage)}': missing 'Review after' or 'Further reading' block"
            )
    return issues


# ── Internal anchors ─────────────────────────────────────────────────────


# Bare-id semantics: a preceding word char or hyphen means this is really
# `data-id="..."`, `aria-labelledby="..."`, etc., not a real `id="..."`
# anchor declaration. Mirrors the lookbehind in
# `check_no_site_wide_id_collisions`.
_ID_RE = re.compile(r'(?<![\w-])id="([\w-]+)"')
_HREF_ANCHOR_RE = re.compile(r'href="#([\w-]+)"')


def check_internal_anchors(html: str) -> list[str]:
    ids = set(_ID_RE.findall(html))
    hrefs = set(_HREF_ANCHOR_RE.findall(html))
    missing = sorted(hrefs - ids)
    return [f"dangling internal anchor: href=\"#{h}\" has no matching id" for h in missing]


# ── Solution blocks ────────────────────────────────────────────────────────

_DETAILS_RE = re.compile(r"<details>(.*?)</details>", re.S)
_SUMMARY_RE = re.compile(r"<summary>(.*?)</summary>", re.S)
_PRE_RE = re.compile(r"<pre>(.*?)</pre>", re.S)
_SOLUTION_SKETCH_RE = re.compile(r"solution sketch", re.IGNORECASE)


def _solution_details(card: Card) -> str | None:
    """Find the `<details>` block whose summary announces the (non-sketch) solution."""
    for m in _DETAILS_RE.finditer(card.body):
        block = m.group(1)
        summary_m = _SUMMARY_RE.search(block)
        summary = summary_m.group(1) if summary_m else ""
        if "solution" in summary.lower() and "sketch" not in summary.lower():
            return block
    return None


def check_solution_block(card: Card) -> list[str]:
    issues: list[str] = []
    if card.tier == TIER_CORE:
        block = _solution_details(card)
        if block is None:
            issues.append(f"{card.id}: core card missing a <details><summary>Solution…</summary> block")
        else:
            pre_m = _PRE_RE.search(block)
            if not pre_m:
                issues.append(f"{card.id}: solution block has no <pre> runnable program")
            else:
                code = strip_html(pre_m.group(1))
                if "fn main" not in code:
                    issues.append(f"{card.id}: solution program is missing `fn main`")
                if not re.search(r"\bassert(?:_eq|_ne)?!\s*\(", code):
                    issues.append(f"{card.id}: solution program has no assert!/assert_eq!/assert_ne! checks")
    elif card.tier == TIER_REINFORCEMENT:
        if not _SOLUTION_SKETCH_RE.search(card.body):
            issues.append(f"{card.id}: reinforcement card missing a 'Solution sketch' block")
    else:
        issues.append(f"{card.id}: invalid or missing data-tier (expected one of {VALID_TIERS})")
    return issues


def extract_runnable(card: Card) -> str | None:
    """Return the stripped Rust source of a core card's solution program, or
    None if it doesn't have one (e.g. reinforcement cards)."""
    block = _solution_details(card)
    if block is None:
        return None
    pre_m = _PRE_RE.search(block)
    if not pre_m:
        return None
    return strip_html(pre_m.group(1))


# ── Compile + run extracted Rust ──────────────────────────────────────────

def compile_and_run_rust(code: str, *, edition: str = "2021", timeout: float = 30.0) -> tuple[bool, str]:
    """Write `code` to a temp dir, compile with rustc, then run the binary.

    Returns (ok, message). `ok` is True only if compilation *and* execution
    (including any assert!/assert_eq! macros) succeed.
    """
    with tempfile.TemporaryDirectory(prefix="learn_track_check_") as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "main.rs"
        binary = tmp_path / ("main.exe" if sys.platform == "win32" else "main")
        src.write_text(code)

        try:
            compiled = subprocess.run(
                ["rustc", f"--edition={edition}", str(src), "-o", str(binary)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError:
            return False, "rustc not found on PATH"
        except subprocess.TimeoutExpired:
            return False, f"rustc timed out after {timeout}s"

        if compiled.returncode != 0:
            return False, f"compile error:\n{compiled.stderr}"

        try:
            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, f"binary timed out after {timeout}s"

        if run.returncode != 0:
            return False, f"runtime failure (exit {run.returncode}):\n{run.stdout}{run.stderr}"

        return True, "ok"


# ── Progress-id self-consistency ──────────────────────────────────────────

_SB_CHECK_RE = re.compile(r'<span class="sb-check" data-id="([\w-]+)"')


def check_progress_id_matches_card(card: Card) -> list[str]:
    m = _SB_CHECK_RE.search(card.body)
    if not m:
        return [f"{card.id}: missing sb-check/progress-id span"]
    if m.group(1) != card.id:
        return [f"{card.id}: sb-check data-id '{m.group(1)}' does not match card id"]
    return []


# ── Whole-track validation ─────────────────────────────────────────────────

@dataclass
class TrackReport:
    spec: TrackSpec
    exists: bool
    issues: list[str] = field(default_factory=list)
    cards: list[Card] = field(default_factory=list)


def validate_track(spec: TrackSpec, html: str | None) -> TrackReport:
    if html is None:
        return TrackReport(spec=spec, exists=False)

    issues: list[str] = []
    cards = parse_cards(html)

    if len(cards) != spec.total:
        issues.append(f"expected {spec.total} exercises for track '{spec.key}', found {len(cards)}")

    worked = [c for c in cards if c.tier == TIER_CORE]
    reinforcement = [c for c in cards if c.tier == TIER_REINFORCEMENT]
    unclassified = [c for c in cards if c.tier not in VALID_TIERS]
    if len(worked) != spec.worked:
        issues.append(
            f"expected {spec.worked} fully worked (core) exercises for track '{spec.key}', found {len(worked)}"
        )
    # Invalid/missing data-tier is reported once per card by check_solution_block
    # below (the per-card loop) — not duplicated here.
    if len(worked) + len(reinforcement) + len(unclassified) != len(cards):
        issues.append("internal error tallying card tiers")  # pragma: no cover — defensive only

    issues += check_labels_ordered(cards, spec.total)
    issues += check_stages(html, spec.prefix)
    issues += check_reading_blocks(html, spec.prefix)
    issues += check_no_lc_chips(html)
    issues += check_internal_anchors(html)

    for card in cards:
        issues += check_required_fields(card)
        issues += check_solution_block(card)
        issues += check_progress_id_matches_card(card)

    return TrackReport(spec=spec, exists=True, issues=issues, cards=cards)


def compile_track_solutions(report: TrackReport) -> list[tuple[str, bool, str]]:
    """Compile + run every core card's solution program. Returns
    (card_id, ok, message) tuples. Only meaningful when report.exists."""
    results = []
    for card in report.cards:
        if card.tier != TIER_CORE:
            continue
        code = extract_runnable(card)
        if code is None:
            results.append((card.id, False, "no runnable program found"))
            continue
        ok, message = compile_and_run_rust(code)
        results.append((card.id, ok, message))
    return results


# ── Cross-track / index.html checks ────────────────────────────────────────

def collect_card_ids(html: str) -> list[str]:
    return [c.id for c in parse_cards(html)]


def check_global_id_uniqueness(track_htmls: dict[str, str]) -> list[str]:
    """No learn-* id may appear in more than one track (or twice within one)."""
    issues: list[str] = []
    seen: dict[str, str] = {}
    for track_key, html in track_htmls.items():
        for cid in collect_card_ids(html):
            if cid in seen:
                issues.append(f"duplicate id '{cid}' in tracks '{seen[cid]}' and '{track_key}'")
            else:
                seen[cid] = track_key
    return issues


def check_no_site_wide_id_collisions(all_html_files: dict[str, str], learn_ids: list[str]) -> list[str]:
    """Every learn-* id must be declared with `id="..."` exactly once across
    the entire site (its own card), even counting files outside the five
    track pages.

    The lookbehind excludes `data-id="..."`, `aria-labelledby="..."`, and any
    other `*-id="..."` attribute — only a bare `id="..."` attribute counts as
    a declaration. Without it, a card's own `data-id` echo of its id (used by
    the sb-check progress span) would be double-counted as a collision.
    """
    issues = []
    for cid in dict.fromkeys(learn_ids):  # dedupe, preserving first-seen order
        pattern = re.compile(rf'(?<![\w-])id="{re.escape(cid)}"')
        occurrences = sum(len(pattern.findall(text)) for text in all_html_files.values())
        if occurrences != 1:
            files = [name for name, text in all_html_files.items() if pattern.search(text)]
            issues.append(f"id '{cid}' declared {occurrences} time(s) across the site (in {files}), expected 1")
    return issues


_MANIFEST_RE_TEMPLATE = r"{var}\s*=\s*\[(.*?)\]"


def check_index_manifest(index_html: str, expected_ids: list[str]) -> list[str]:
    pattern = re.compile(_MANIFEST_RE_TEMPLATE.format(var=re.escape(MANIFEST_VAR)), re.S)
    m = pattern.search(index_html)
    if not m:
        return [f"index.html: could not find `{MANIFEST_VAR} = [...]` progress manifest"]

    found_ids = re.findall(r'["\']([\w-]+)["\']', m.group(1))
    found_set, expected_set = set(found_ids), set(expected_ids)

    issues: list[str] = []
    missing = sorted(expected_set - found_set)
    extra = sorted(found_set - expected_set)
    for cid in missing:
        issues.append(f"index.html manifest missing id '{cid}'")
    for cid in extra:
        issues.append(f"index.html manifest has unexpected id '{cid}'")

    dupes = sorted({cid for cid in found_ids if found_ids.count(cid) > 1})
    for cid in dupes:
        issues.append(f"index.html manifest lists id '{cid}' more than once")

    return issues


# ── CLI ─────────────────────────────────────────────────────────────────

def _load_track_htmls(root: Path) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for spec in TRACKS:
        p = root / spec.filename
        result[spec.key] = p.read_text() if p.exists() else None
    return result


def _load_all_html_files(root: Path) -> dict[str, str]:
    return {p.name: p.read_text() for p in root.glob("*.html")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT), help="directory containing the track HTML files")
    parser.add_argument("--compile", action="store_true", help="also compile & run every core solution (slow)")
    parser.add_argument("--track", choices=[t.key for t in TRACKS], help="only validate one track")
    args = parser.parse_args(argv)

    root = Path(args.root)
    specs = [t for t in TRACKS if args.track is None or t.key == args.track]

    track_htmls_all = _load_track_htmls(root)
    any_failures = False
    any_present = False

    reports: dict[str, TrackReport] = {}
    for spec in specs:
        html = track_htmls_all[spec.key]
        report = validate_track(spec, html)
        reports[spec.key] = report

        print(f"\n== {spec.key} ({spec.filename}) ==")
        if not report.exists:
            print("  SKIP: file not found (not authored yet)")
            continue
        any_present = True
        if not report.issues:
            print(f"  PASS: {spec.total} exercises, {spec.worked} fully worked, all checks green")
        else:
            any_failures = True
            for issue in report.issues:
                print(f"  FAIL: {issue}")

        if args.compile:
            for cid, ok, message in compile_track_solutions(report):
                if ok:
                    print(f"  COMPILE OK: {cid}")
                else:
                    any_failures = True
                    print(f"  COMPILE FAIL: {cid}: {message}")

    if args.track is None and any_present:
        present_htmls = {k: v for k, v in track_htmls_all.items() if v is not None}
        print("\n== cross-track checks ==")
        dupe_issues = check_global_id_uniqueness(present_htmls)
        for issue in dupe_issues:
            any_failures = True
            print(f"  FAIL: {issue}")

        all_learn_ids = [cid for html in present_htmls.values() for cid in collect_card_ids(html)]
        all_html_files = _load_all_html_files(root)
        collision_issues = check_no_site_wide_id_collisions(all_html_files, all_learn_ids)
        for issue in collision_issues:
            any_failures = True
            print(f"  FAIL: {issue}")

        if len(present_htmls) == len(TRACKS):
            index_path = root / "index.html"
            if index_path.exists():
                manifest_issues = check_index_manifest(index_path.read_text(), all_learn_ids)
                for issue in manifest_issues:
                    any_failures = True
                    print(f"  FAIL: {issue}")
            else:
                print("  SKIP: index.html not found")
        else:
            print("  SKIP: progress-manifest parity (not all five tracks are authored yet)")

    print()
    if any_failures:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS (or nothing to check yet)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
