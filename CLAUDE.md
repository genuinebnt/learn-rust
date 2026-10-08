# anneal

Personal Rust interview-prep platform: axum API (`crates/api`), sandboxed runner (`crates/runner`), file-based
content (`content/tracks`), React SPA (`web`).

**Start with [docs/HANDOFF.md](docs/HANDOFF.md).** It covers the current state, how to run and check the work,
the owner's working rules, and the pending work in order. **§6.0 is the pick-up point**: what's unfinished per track,
a checklist of every problem not yet written, and the agent instructions in [docs/authoring/](docs/authoring/).

The rules that matter most:

- Do only what's asked. Propose extras with a recommendation and wait. Never drop existing controls.
- Mock up new screens and big UI changes in HTML and get approval before building them.
- No visible scrollbars. 4-space indent. Don't run prettier (there's no config; match the surrounding style).
- Check content with `cargo run -q -p anneal-cli -- verify <track>`, which works without Docker.
- End commit messages with the `Co-Authored-By` line for your model.
- Courses (`courses/`, the Courses pages): read [docs/COURSE_STANDARDS.md](docs/COURSE_STANDARDS.md) first and run `anneal course lint`. Do not rebuild from memory what the owner has already decided.
