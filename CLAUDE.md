# anneal

Personal Rust interview-prep platform: axum API (`crates/api`), sandboxed runner (`crates/runner`), file-based
content (`content/tracks`), React SPA (`web`).

**Start with [docs/HANDOFF.md](docs/HANDOFF.md).** It covers the current state, how to run and check the work,
the owner's working rules, and the pending work in order.

The rules that matter most:

- Do only what's asked. Propose extras with a recommendation and wait. Never drop existing controls.
- Mock up new screens and big UI changes in HTML and get approval before building them.
- No visible scrollbars. 4-space indent. Don't run prettier (there's no config; match the surrounding style).
- Check content with `cargo run -q -p anneal-cli -- verify <track>`, which works without Docker.
- End commit messages with the `Co-Authored-By` line for your model.
