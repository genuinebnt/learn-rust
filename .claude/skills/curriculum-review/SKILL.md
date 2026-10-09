---
name: curriculum-review
description: Audit or write course content (stage.md, concept articles, tracks) against the owner's mentor-grade standard: career outcome, prose quality, exercises worth completing, mastery coverage, verification. Use when asked to reassess, audit, improve or extend a course, a module, a track or a lesson, or before shipping new course content.
---

# Curriculum review

Use with docs/COURSE_STANDARDS.md (the owner's decisions), docs/CURRICULUM_REASSESSMENT.md (the current findings and plan) and docs/authoring/*.md (how to write). This skill adds the review procedure and rubric. It draws on the generate-then-verify discipline and prose rules of `course-generator` (cat-xierluo, MIT) and on `learning-tutor` (event4u-app, MIT); nothing is copied.

## The outcome everything is judged against

The owner wants to be hired as a database engineer at a top database company (Rust or C++ shops: storage engines, query engines, distributed databases). After a module they must be able to: build it from a blank file, explain the trade-offs aloud, predict what a change does, debug it, and measure it. A lesson that only lets them recognise the answer has failed.

## Procedure

1. **Name the competency.** One sentence: "after this, the owner can ...". If you cannot write it, the content has no job.
2. **Measure first, then read.** Script the counts (words, prose words versus bullet and table lines, headings, exercises, hints, tests, assertion messages, `given` mentions, links to concepts). Then read at least three samples in full, the best, a median and the worst.
3. **Score against the rubric** below, with evidence (file and line), not impressions.
4. **Verify independently.** The author does not verify their own work. Run `anneal course lint`, `anneal course verify`, `tools/course_snippets.py` and `tools/check_course_links.py`, and give a fresh reader (a subagent, or you after a break with only the page) the page and ask what they would do first, where they would be stuck and what they could not do after reading.
5. **Report findings ranked by what they cost the learner**, then propose fixes with a recommendation and wait. Do not rewrite content nobody asked about.

## Rubric (each item pass / partial / fail, with evidence)

**Teaching quality**
- *Prose.* Explanations are connected paragraphs that start from the problem, build the idea, show a worked example with real numbers and name the failure mode. Bullets and tables carry parallel facts, not reasoning. A concept article should be at least half prose by words.
- *Accuracy.* Every claim about a system (Rust, BusTub, Postgres, RocksDB, the OS) is checked; numbers are measured or hedged; links work.
- *Level.* States what is assumed; defines each term once at first use; no unexplained jump.

**Exercises**
- *Worth completing.* Each exercise needs a design decision or a debugging step, tests that fail with a message naming the behaviour, and a reason the owner would not skip it.
- *Contract not recipe.* The task states behaviour and invariants; steps live in a collapsed aside; hints give the why.
- *Design left open* where the idea is the lesson; "given" scaffolding only for plumbing.
- *Retrieval.* Open check-yourself questions (never multiple choice), a rebuild-from-blank kata after each module and a spaced return a week later.
- *Experiments.* Predict, change one thing, measure, explain.

**Mastery coverage**
- Syntax and semantics (what the code means, not just that it compiles), logical thinking (invariants, proofs by case, reading code), problem solving (decomposition, small cases first, estimation), systems knowledge (OS, memory, I/O, concurrency, hardware costs), database knowledge (storage, indexing, execution, optimisation, transactions, recovery, distribution).
- Each is traced to stages or tracks; gaps are listed, not hidden.

**Career alignment**
- Interview-style questions for the topic (explain it, whiteboard it, trade-offs, failure modes), one portfolio-grade artefact per project (code, benchmark, write-up), and a link to a real open-source system where the idea lives.

## Prose rules (the owner asked for very high quality prose)

- Open with why: the problem the idea solves, in one concrete scene (a crash mid-write, two threads on one page).
- Introduce a term only when it is needed, and say it once in plain words before using it.
- One idea per paragraph; show the reasoning step, not the conclusion.
- Use a running example with numbers; keep it through the article.
- Say what goes wrong and how you would notice.
- End with what to try (an experiment or a question), not a summary.
- No filler, no hype, no "simply" or "just"; keep the voice of a patient senior engineer.

## Output

A short report: scores with evidence, the five costliest problems, a proposed change list in recommended order, and the checks that must pass before shipping. Save it under docs/ only if the owner asks.
