# anneal · AI assistant

An **AI** tab in the workspace's right panel and a **Your patterns** tab on the Progress page. The approved mockup
is `design_handoff_anneal/designs/ai-assistant.html`. It's built on [rig](https://rig.rs) (`rig-core`).

## Turning it on

**In the app:** open the AI tab on any problem (or Progress → Your patterns), choose a provider, paste the key and
press **Test & save**. The server checks it with a tiny request, stores it in the `settings` table under `ai`, and
switches the assistant on without a restart. The browser never gets the key back, only its last four characters;
**key** in the AI tab's header changes or removes it. Errors are scrubbed of keys before they're shown or logged
(Gemini sends its key in the URL).

**Or on the server:** a key in the environment works as a fallback when none is saved in the app.

| Where | How |
|---|---|
| Local (`scripts/dev.sh`) | `GEMINI_API_KEY=…` in `.env.local` at the repo root (git-ignored), then restart |
| Production | `GEMINI_API_KEY=…` in `~/anneal/deploy/.env` on the VM, then redeploy |

| Variable | Meaning |
|---|---|
| `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` | a provider's key; any one turns the assistant on |
| `ANNEAL_AI_PROVIDER` | `gemini`, `openai` or `anthropic`; default: the first of those with a key |
| `ANNEAL_AI_MODEL` | chat model; defaults `gemini-3.8-flash`, `gpt-5.5`, `claude-sonnet-4-6` |
| `ANNEAL_AI_EMBED_PROVIDER` | `gemini`, `openai` or `none`; default: the chat provider if it has embeddings (Anthropic doesn't), else another with a key |
| `ANNEAL_AI_EMBED_MODEL` | defaults `gemini-embedding-001`, `text-embedding-3-small` |

Switching to OpenAI or Claude later means setting that key and `ANNEAL_AI_PROVIDER`; nothing else changes. With no
embedding provider, similar problems fall back to shared tags.

## What it does

- **Chat per problem** (`POST /api/ai/chat/{id}`, server-sent events), saved in `ai_messages`. Quick actions:
  - explain this error;
  - hint;
  - complexity;
  - how did I do on similar ones;
  - review (after a solve).
- **Grounding (RAG).** Every answer gets these documents, and the UI shows each one as a chip under the answer:
  - the problem;
  - the editor's current code;
  - the last run: errors with rustc's rendering, and failing tests with got/expected or the panic;
  - the reference solution, **only once you've solved it or revealed it**;
  - similar problems, with how you did on them;
  - your past attempts closest to the question;
  - your stats: first-run pass rate, runs per solve, top errors and lints, and where they cluster.
- **Embeddings.** Every problem and every attempt you've run code in is embedded once. It's embedded again only
  when its text changes, which is checked with an FNV hash. The vectors live in `ai_embeddings` as `real[]` and are
  searched in memory: at a few thousand rows that's instant, and it needs no Postgres extension. Indexing runs at
  startup and after each solve.
- **Your patterns** (`/api/ai/patterns`). The model writes 4–6 observations and picks three problems to practise
  next from candidates anneal chooses. The numbers are computed exactly by anneal: attempts, runs, and where
  failing runs went (borrow checker, other compile errors, failing tests, timeouts).

## Honest progress

Any AI help before a solve marks the current attempt **assisted**, the same as a hint, so spaced repetition and
readiness aren't fooled. The panel says so. After a solve, help is free.

## Code

- `crates/ai` (`anneal-ai`, edition 2024): the provider enum over rig's clients, streaming chat, embeddings and
  cosine similarity.
- `crates/api/src/ai/`:
  - `mod.rs`: routes and the chat stream;
  - `context.rs`: grounding;
  - `index.rs`: embeddings;
  - `report.rs`: the patterns report.
- `web/src/workspace/AiPanel.tsx`: the panel. `aimd.ts` renders answers as Markdown without trusting their HTML.
  The Patterns tab is in `pages/ProgressPage.tsx`.
- Migration `0006_ai.sql`. `ai_messages` is progress, so renames move it and preflight counts it
  (`preflight.rs`).
