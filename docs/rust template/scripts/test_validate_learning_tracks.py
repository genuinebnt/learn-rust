"""Executable spec for validate_learning_tracks.py — the learning-track contract.

Run with:
    python3 -m unittest test_validate_learning_tracks -v
(from `rust template/scripts/`), or:
    python3 "rust template/scripts/test_validate_learning_tracks.py"
(from the repo root).

These tests define the HTML/ID/progress-manifest contract that the five
`part-learn-*.html` pages must satisfy before any of that content exists.
Every fixture below is an in-memory string — no track HTML files are created
in the repo by this suite.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_learning_tracks as vlt

# ── Fixture builders ─────────────────────────────────────────────────────
# A minimal "valid" track uses a tiny synthetic TrackSpec (2 exercises: one
# core/fully-worked, one reinforcement) so tests stay fast and don't need to
# fabricate 24-80 real exercises. The *shape* of each card/stage/reading
# block below is exactly what real track authors must reproduce.

MINI_SPEC = vlt.TrackSpec(
    key="mini", prefix="learn-mini", filename="part-learn-mini.html", total=2, worked=1
)


def reading_block(label: str, text: str = "See chapter X.") -> str:
    return f'<div class="note"><strong>{label}:</strong> {text}</div>'


def stage_section(prefix: str, stage: str, body: str) -> str:
    stage_id = f"{prefix}-stage-{stage.lower()}"
    return f"""
<div class="section" id="{stage_id}">
  <div class="section-header">
    <div class="sh-bar"></div>
    <div>
      <div class="sh-eyebrow">// Learning · {stage}</div>
      <div class="sh-title">{stage}</div>
    </div>
  </div>
  {reading_block("Read before")}
  {reading_block("Review after")}
  {body}
</div>
"""


def required_fields_block() -> str:
    return "".join(f'<div class="note"><strong>{f}:</strong> text.</div>' for f in vlt.REQUIRED_FIELDS)


def core_card(prefix: str, seq: int, *, rust_code: str | None = None) -> str:
    cid = f"{prefix}-{seq:02d}"
    label = f"Learning {seq:02d}"
    code = rust_code or (
        "fn main() {\n"
        "    assert_eq!(1 + 1, 2);\n"
        "}"
    )
    fields = required_fields_block()
    return f"""
<div class="card" id="{cid}" data-tier="core">
  <div class="ex-meta">
    <span class="chip">recursion</span>
    <span class="chip chip-easy">{label}</span>
  </div>
  <div class="card-label">Title<span class="sb-check" data-id="{cid}" onclick="toggleDone(event,'{cid}')"></span></div>
  {fields}
  <details>
    <summary>Solution — reveal after attempting</summary>
    <div><pre>{code}</pre></div>
  </details>
</div>
"""


def reinforcement_card(prefix: str, seq: int) -> str:
    cid = f"{prefix}-{seq:02d}"
    label = f"Learning {seq:02d}"
    fields = required_fields_block()
    return f"""
<div class="card" id="{cid}" data-tier="reinforcement">
  <div class="ex-meta">
    <span class="chip">recursion</span>
    <span class="chip chip-medium">{label}</span>
  </div>
  <div class="card-label">Title<span class="sb-check" data-id="{cid}" onclick="toggleDone(event,'{cid}')"></span></div>
  {fields}
  <div class="note"><strong>Solution sketch:</strong> outline only, no full program.</div>
</div>
"""


def invalid_tier_card(prefix: str, seq: int) -> str:
    """A card missing (or with an unrecognized) `data-tier` — otherwise complete."""
    cid = f"{prefix}-{seq:02d}"
    label = f"Learning {seq:02d}"
    fields = required_fields_block()
    return f"""
<div class="card" id="{cid}">
  <div class="ex-meta">
    <span class="chip">recursion</span>
    <span class="chip chip-easy">{label}</span>
  </div>
  <div class="card-label">Title<span class="sb-check" data-id="{cid}" onclick="toggleDone(event,'{cid}')"></span></div>
  {fields}
</div>
"""


def build_valid_mini_track() -> str:
    foundation = stage_section(MINI_SPEC.prefix, "Foundation", "<p>intro</p>")
    easy = stage_section(MINI_SPEC.prefix, "Easy", core_card(MINI_SPEC.prefix, 1))
    medium = stage_section(MINI_SPEC.prefix, "Medium", reinforcement_card(MINI_SPEC.prefix, 2))
    hard = stage_section(MINI_SPEC.prefix, "Hard", "<p>none yet</p>")
    mastery = stage_section(MINI_SPEC.prefix, "Mastery", reading_block("Further reading"))
    return foundation + easy + medium + hard + mastery


VALID_MINI_TRACK_HTML = build_valid_mini_track()


# ── Contract constants ───────────────────────────────────────────────────

class TrackSpecsTests(unittest.TestCase):
    def test_track_counts_match_plan(self):
        expected = {
            "linked-lists": (24, 12),
            "trees": (50, 24),
            "tries": (20, 10),
            "graphs": (70, 30),
            "dp": (80, 32),
        }
        actual = {t.key: (t.total, t.worked) for t in vlt.TRACKS}
        self.assertEqual(actual, expected)

    def test_grand_totals(self):
        self.assertEqual(vlt.TOTAL_EXERCISES, 244)
        self.assertEqual(vlt.TOTAL_WORKED, 108)

    def test_five_stages_in_order(self):
        self.assertEqual(vlt.STAGES, ("Foundation", "Easy", "Medium", "Hard", "Mastery"))


# ── Card parsing ─────────────────────────────────────────────────────────

class ParseCardsTests(unittest.TestCase):
    def test_parses_id_tier_and_label(self):
        cards = vlt.parse_cards(VALID_MINI_TRACK_HTML)
        self.assertEqual([c.id for c in cards], ["learn-mini-01", "learn-mini-02"])
        self.assertEqual(cards[0].tier, "core")
        self.assertEqual(cards[1].tier, "reinforcement")
        self.assertEqual(cards[0].seq, 1)
        self.assertIn("Learning 01", cards[0].label or "")

    def test_no_cards_in_empty_html(self):
        self.assertEqual(vlt.parse_cards("<div>nothing here</div>"), [])


# ── Label / ID ordering ──────────────────────────────────────────────────

class LabelOrderingTests(unittest.TestCase):
    def test_sequential_labels_pass(self):
        cards = vlt.parse_cards(VALID_MINI_TRACK_HTML)
        self.assertEqual(vlt.check_labels_ordered(cards, MINI_SPEC.total), [])

    def test_out_of_order_labels_fail(self):
        bad_html = core_card("learn-mini", 2) + core_card("learn-mini", 1)
        cards = vlt.parse_cards(bad_html)
        issues = vlt.check_labels_ordered(cards, MINI_SPEC.total)
        self.assertTrue(issues, "expected ordering issue to be reported")

    def test_gap_in_sequence_fails(self):
        bad_html = core_card("learn-mini", 1) + core_card("learn-mini", 3)
        cards = vlt.parse_cards(bad_html)
        issues = vlt.check_labels_ordered(cards, 2)
        self.assertTrue(issues)


# ── Required metadata fields ─────────────────────────────────────────────

class RequiredFieldsTests(unittest.TestCase):
    def test_complete_card_has_no_issues(self):
        cards = vlt.parse_cards(VALID_MINI_TRACK_HTML)
        self.assertEqual(vlt.check_required_fields(cards[0]), [])

    def test_missing_field_is_reported(self):
        html = core_card("learn-mini", 1).replace(
            '<div class="note"><strong>Unlocks next:</strong> text.</div>', ""
        )
        card = vlt.parse_cards(html)[0]
        issues = vlt.check_required_fields(card)
        self.assertTrue(any("Unlocks next" in i for i in issues))


# ── No LeetCode-number chips ──────────────────────────────────────────────

class NoLcChipTests(unittest.TestCase):
    def test_clean_html_passes(self):
        self.assertEqual(vlt.check_no_lc_chips(VALID_MINI_TRACK_HTML), [])

    def test_lc_chip_is_flagged(self):
        html = VALID_MINI_TRACK_HTML + '<span class="chip">LC 42</span>'
        issues = vlt.check_no_lc_chips(html)
        self.assertTrue(issues)


# ── Stage sections ────────────────────────────────────────────────────────

class StageSectionTests(unittest.TestCase):
    def test_all_five_stages_present_and_ordered(self):
        issues = vlt.check_stages(VALID_MINI_TRACK_HTML, MINI_SPEC.prefix)
        self.assertEqual(issues, [])

    def test_missing_stage_is_reported(self):
        html = VALID_MINI_TRACK_HTML.replace(
            f'<div class="section" id="{MINI_SPEC.prefix}-stage-hard">',
            '<div class="section" id="learn-mini-stage-removed">',
        )
        issues = vlt.check_stages(html, MINI_SPEC.prefix)
        self.assertTrue(any("Hard" in i for i in issues))

    def test_out_of_order_stages_reported(self):
        foundation = stage_section(MINI_SPEC.prefix, "Foundation", "")
        easy = stage_section(MINI_SPEC.prefix, "Easy", "")
        hard = stage_section(MINI_SPEC.prefix, "Hard", "")
        medium = stage_section(MINI_SPEC.prefix, "Medium", "")
        mastery = stage_section(MINI_SPEC.prefix, "Mastery", "")
        # Hard placed before Medium — wrong order.
        html = foundation + easy + hard + medium + mastery
        issues = vlt.check_stages(html, MINI_SPEC.prefix)
        self.assertTrue(any("order" in i.lower() for i in issues))


# ── Reading blocks ────────────────────────────────────────────────────────

class ReadingBlockTests(unittest.TestCase):
    def test_valid_track_has_no_reading_issues(self):
        issues = vlt.check_reading_blocks(VALID_MINI_TRACK_HTML, MINI_SPEC.prefix)
        self.assertEqual(issues, [])

    def test_missing_read_before_is_reported(self):
        html = VALID_MINI_TRACK_HTML.replace(reading_block("Read before"), "", 1)
        issues = vlt.check_reading_blocks(html, MINI_SPEC.prefix)
        self.assertTrue(any("Read before" in i for i in issues))


# ── Internal anchors ──────────────────────────────────────────────────────

class InternalAnchorTests(unittest.TestCase):
    def test_no_dangling_anchors_in_valid_track(self):
        self.assertEqual(vlt.check_internal_anchors(VALID_MINI_TRACK_HTML), [])

    def test_dangling_anchor_is_reported(self):
        html = VALID_MINI_TRACK_HTML + '<a href="#does-not-exist">jump</a>'
        issues = vlt.check_internal_anchors(html)
        self.assertTrue(any("does-not-exist" in i for i in issues))

    def test_data_id_alone_does_not_satisfy_an_anchor(self):
        # `data-id="missing"` is a progress-tracking attribute, not a real
        # `id="missing"` anchor declaration — a card that only carries the
        # former must still be reported as a dangling anchor target.
        html = (
            '<a href="#missing">jump</a>'
            '<div class="card"><span class="sb-check" data-id="missing"></span></div>'
        )
        issues = vlt.check_internal_anchors(html)
        self.assertTrue(any("missing" in i for i in issues), issues)


# ── Solution blocks (core = runnable program, reinforcement = sketch) ────

class SolutionBlockTests(unittest.TestCase):
    def test_core_card_with_runnable_program_passes(self):
        cards = vlt.parse_cards(VALID_MINI_TRACK_HTML)
        core = next(c for c in cards if c.tier == vlt.TIER_CORE)
        self.assertEqual(vlt.check_solution_block(core), [])

    def test_core_card_without_program_fails(self):
        html = core_card("learn-mini", 1, rust_code="// just a sketch, no fn main")
        card = vlt.parse_cards(html)[0]
        issues = vlt.check_solution_block(card)
        self.assertTrue(issues)

    def test_reinforcement_card_with_sketch_passes(self):
        cards = vlt.parse_cards(VALID_MINI_TRACK_HTML)
        reinforcement = next(c for c in cards if c.tier == vlt.TIER_REINFORCEMENT)
        self.assertEqual(vlt.check_solution_block(reinforcement), [])

    def test_reinforcement_card_without_sketch_fails(self):
        html = reinforcement_card("learn-mini", 2).replace(
            '<div class="note"><strong>Solution sketch:</strong> outline only, no full program.</div>',
            "",
        )
        card = vlt.parse_cards(html)[0]
        issues = vlt.check_solution_block(card)
        self.assertTrue(issues)

    def test_invalid_tier_card_reports_one_issue_when_called_directly(self):
        # Direct callers of check_solution_block still need to learn about an
        # invalid/missing data-tier — only validate_track's aggregation must
        # avoid double-reporting it (see ValidateTrackIntegrationTests).
        card = vlt.parse_cards(invalid_tier_card("learn-mini", 1))[0]
        issues = vlt.check_solution_block(card)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("data-tier", issues[0])


# ── Rust extraction + compilation ────────────────────────────────────────

class CompileRunnableRustTests(unittest.TestCase):
    def test_extract_runnable_returns_stripped_source(self):
        cards = vlt.parse_cards(VALID_MINI_TRACK_HTML)
        core = next(c for c in cards if c.tier == vlt.TIER_CORE)
        code = vlt.extract_runnable(core)
        self.assertIsNotNone(code)
        self.assertIn("fn main()", code)
        self.assertIn("assert_eq!(1 + 1, 2)", code)
        self.assertNotIn("<span", code)  # was stripped of highlighting markup

    def test_compile_and_run_passing_program(self):
        ok, message = vlt.compile_and_run_rust("fn main() { assert_eq!(2 + 2, 4); }")
        self.assertTrue(ok, message)

    def test_compile_and_run_reports_compile_error(self):
        ok, message = vlt.compile_and_run_rust("fn main() { this is not rust }")
        self.assertFalse(ok)
        self.assertIn("error", message.lower())

    def test_compile_and_run_reports_assertion_failure(self):
        ok, message = vlt.compile_and_run_rust("fn main() { assert_eq!(1, 2); }")
        self.assertFalse(ok)


# ── Card-level self-consistency (progress id == card id) ─────────────────

class ProgressIdConsistencyTests(unittest.TestCase):
    def test_matching_progress_id_passes(self):
        cards = vlt.parse_cards(VALID_MINI_TRACK_HTML)
        self.assertEqual(vlt.check_progress_id_matches_card(cards[0]), [])

    def test_mismatched_progress_id_fails(self):
        html = core_card("learn-mini", 1).replace(
            'data-id="learn-mini-01"', 'data-id="learn-mini-99"'
        )
        card = vlt.parse_cards(html)[0]
        issues = vlt.check_progress_id_matches_card(card)
        self.assertTrue(issues)


# ── Whole-track integration ──────────────────────────────────────────────

class ValidateTrackIntegrationTests(unittest.TestCase):
    def test_valid_mini_track_has_zero_issues(self):
        report = vlt.validate_track(MINI_SPEC, VALID_MINI_TRACK_HTML)
        self.assertTrue(report.exists)
        self.assertEqual(report.issues, [], report.issues)

    def test_missing_file_reports_not_exists_without_crashing(self):
        report = vlt.validate_track(MINI_SPEC, None)
        self.assertFalse(report.exists)
        self.assertEqual(report.issues, [])

    def test_wrong_exercise_count_is_reported(self):
        html = core_card("learn-mini", 1)  # only 1 card, spec expects 2
        report = vlt.validate_track(MINI_SPEC, html)
        self.assertTrue(any("exercise" in i.lower() for i in report.issues))

    def test_wrong_worked_count_is_reported(self):
        html = core_card("learn-mini", 1) + core_card("learn-mini", 2)  # both core, spec wants 1 worked
        report = vlt.validate_track(MINI_SPEC, html)
        self.assertTrue(any("worked" in i.lower() or "fully" in i.lower() for i in report.issues))

    def test_invalid_tier_reported_exactly_once(self):
        # Previously reported twice: once by validate_track's own unclassified-
        # tier loop, and again by check_solution_block's per-card pass.
        html = invalid_tier_card("learn-mini", 1) + reinforcement_card("learn-mini", 2)
        report = vlt.validate_track(MINI_SPEC, html)
        tier_issues = [i for i in report.issues if "data-tier" in i]
        self.assertEqual(len(tier_issues), 1, tier_issues)


# ── Global ID uniqueness across tracks ────────────────────────────────────

class GlobalIdUniquenessTests(unittest.TestCase):
    def test_unique_ids_across_tracks_pass(self):
        track_htmls = {"a": core_card("learn-a", 1), "b": core_card("learn-b", 1)}
        self.assertEqual(vlt.check_global_id_uniqueness(track_htmls), [])

    def test_duplicate_ids_across_tracks_fail(self):
        track_htmls = {"a": core_card("learn-dup", 1), "b": core_card("learn-dup", 1)}
        issues = vlt.check_global_id_uniqueness(track_htmls)
        self.assertTrue(issues)


# ── Site-wide id-declaration collisions (id= vs data-id=) ────────────────

class SiteWideIdCollisionTests(unittest.TestCase):
    def test_card_with_matching_data_id_counts_as_one_declaration(self):
        # A normal, valid core card declares both `id="learn-mini-01"` (the
        # card element itself) and `data-id="learn-mini-01"` (its sb-check
        # progress span, per contract). The data-id echo must NOT be counted
        # as a second `id=` declaration of the same id.
        html = core_card("learn-mini", 1)
        issues = vlt.check_no_site_wide_id_collisions({"file.html": html}, ["learn-mini-01"])
        self.assertEqual(issues, [])

    def test_true_duplicate_id_declaration_is_reported(self):
        html_a = '<div class="card" id="learn-dup-01">A</div>'
        html_b = '<div class="card" id="learn-dup-01">B</div>'
        issues = vlt.check_no_site_wide_id_collisions(
            {"a.html": html_a, "b.html": html_b}, ["learn-dup-01"]
        )
        self.assertTrue(any("learn-dup-01" in i for i in issues))

    def test_duplicate_input_ids_do_not_duplicate_the_issue_message(self):
        # collect_card_ids can legitimately hand the same id to this function
        # more than once (e.g. callers concatenating per-track id lists); the
        # collision report itself must still be deduped to one message.
        html_a = '<div class="card" id="learn-dup-01">A</div>'
        html_b = '<div class="card" id="learn-dup-01">B</div>'
        issues = vlt.check_no_site_wide_id_collisions(
            {"a.html": html_a, "b.html": html_b}, ["learn-dup-01", "learn-dup-01"]
        )
        self.assertEqual(len(issues), 1, issues)


# ── index.html progress-manifest parity ──────────────────────────────────

class IndexManifestParityTests(unittest.TestCase):
    def test_matching_manifest_passes(self):
        index_html = f'<script>const {vlt.MANIFEST_VAR} = ["learn-mini-01", "learn-mini-02"];</script>'
        issues = vlt.check_index_manifest(index_html, ["learn-mini-01", "learn-mini-02"])
        self.assertEqual(issues, [])

    def test_missing_manifest_entry_reported(self):
        index_html = f'<script>const {vlt.MANIFEST_VAR} = ["learn-mini-01"];</script>'
        issues = vlt.check_index_manifest(index_html, ["learn-mini-01", "learn-mini-02"])
        self.assertTrue(any("learn-mini-02" in i for i in issues))

    def test_extra_manifest_entry_reported(self):
        index_html = f'<script>const {vlt.MANIFEST_VAR} = ["learn-mini-01", "learn-mini-02", "learn-mini-99"];</script>'
        issues = vlt.check_index_manifest(index_html, ["learn-mini-01", "learn-mini-02"])
        self.assertTrue(any("learn-mini-99" in i for i in issues))

    def test_absent_manifest_variable_reported(self):
        issues = vlt.check_index_manifest("<script>// nothing here</script>", ["learn-mini-01"])
        self.assertTrue(issues)


if __name__ == "__main__":
    unittest.main()
