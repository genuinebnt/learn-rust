# Curriculum reassessment: a mentor's view (2026-10-09)

Written at the owner's request, as a mentor whose job is to get the owner hired as a database engineer at a top database company, and to make them genuinely good at systems programming, Rust, logical thinking and problem solving on the way. It uses the two project skills added the same day ([mentor-teaching](../.claude/skills/mentor-teaching/SKILL.md) and [curriculum-review](../.claude/skills/curriculum-review/SKILL.md)), which draw on the `learning-tutor` skill (event4u-app, MIT) and the `course-generator` skill (cat-xierluo, MIT). Neither was copied; the course-generator turns source documents into courses, so only its prose and verify-separately rules apply here. There is no skill called "claude teach"; `learning-tutor` is the nearest thing and its structure is what the mentor skill follows.

Method: counts from scripts over all 163 stage files, 117 concept articles, the reference tests and the track list, plus full reads of a best, a median and a weak sample. Nothing here is a claim about how well it works for you in practice yet; section 7 says how to find out.

## 1. What a job at a database company asks for

I cannot promise a salary. What can be controlled is the evidence a hiring team sees. From what such interviews and job descriptions usually contain (check current openings before leaning on any one):

| Competency | What shows it | Where it lives here today | Gap |
|---|---|---|---|
| Data structures and algorithms under time pressure | medium and hard problems, explained aloud | D1–D18 (all 18 NeetCode topics, 596 Rust problems) | few "explain your trade-offs" drills |
| Rust fluency (ownership, traits, generics, errors, iterators, closures, smart pointers) | idiomatic code, no fighting the compiler | L1–L5, S1–S4 written; BusTub teaches by use | L6–L10, S5–S11 unwritten; the concepts audit lists missing articles (smart pointers, `Send`/`Sync`, type-driven design, iterators) |
| Systems programming: memory, files, syscalls, virtual memory, `fsync`, `mmap`, I/O costs | explaining what happens between `write` and the disk | pieces in BusTub 1a/1f and `durability-and-fsync` | SYSTEMS.md K1–K24 are designed, none written |
| Concurrency: locks, latches, atomics, memory ordering, lock-free basics | finding a deadlock, choosing an ordering | BusTub 1b, 1g, 2b, 2c-09; 11 concept articles | C1–C5 (threads, channels, atomics, async) unwritten; no `Send`/`Sync`; no Tokio |
| Storage engines: pages, buffer pool, B+ tree | building one | BusTub 1a–1g, 2a–2d (strong) | no LSM tree, SSTables, compaction |
| Query execution and optimisation | executors, joins, sort, aggregation, rules | BusTub 3a–3h (strong) | no cost-based optimisation or statistics; no columnar or vectorised execution; no SQL parsing |
| Transactions and recovery | MVCC, isolation anomalies, WAL, ARIES | 4a–4b (MVCC, GC, validation) | **no logging, checkpoints or crash recovery**; no 2PL or OCC comparison |
| Distributed systems | replication, consensus, partitioning | 0d (CRDT primer) only | no Raft, no replication, no sharding |
| Performance engineering | profiling, cache effects, benchmarks | one Performance section per stage; F2 data layout | no profiling track; no SIMD; no benchmark harness habit |
| Evidence of ability | a public project, a write-up, an open-source contribution | none yet | the capstone and contribution plan (section 5) |

The honest summary: BusTub covers the middle of a single-node relational engine very well. The three biggest holes for the roles you want are **recovery**, **LSM-based storage** and **distributed consensus**, and the biggest hole for the general-skill goals is that most of the Rust and systems tracks are designed but not yet written.

## 2. What the learning research says, and what it changes here

From the literature as I know it (I have not re-checked sources this session; each is a well-replicated finding, with effect sizes that vary):

- **Retrieval practice** (Roediger and Karpicke, 2006): trying to recall beats rereading. Hence open check-yourself questions and blank-file rebuilds, not recognition quizzes. Simple multiple choice is the weakest form, which agrees with your dislike of it.
- **Generation effect** (Slamecka and Graf, 1978) and **pre-testing** (Richland and others, 2009): producing an answer, even a wrong one, before seeing it makes the later explanation stick. Hence "predict first" prompts and tasks that state behaviour, not steps.
- **Desirable difficulties** (Bjork): a little more struggle slows practice and improves retention. The risk is the **illusion of competence** from reading a solution, which is exactly what copying BusTub's reference code produces.
- **Worked examples, fading and expertise reversal** (Sweller, Kalyuga): beginners learn faster from full examples; as skill grows the same help hurts. So scaffolding must fade: heavy in 1a, light by project 4. Today it does the opposite (section 3).
- **Productive failure** (Kapur): attempting a problem before instruction can beat instruction first for concept learning, if followed by consolidation.
- **Spacing and interleaving** (Cepeda; Rohrer): revisiting after days beats massing. The platform has spaced review for DSA ([SPACED_REPETITION.md](SPACED_REPETITION.md)) but not for course content.
- **Self-explanation and the Feynman method** (Chi): explaining why a step works finds gaps. A mock-interview habit on top of the BusTub stages covers this.
- **Deliberate practice** (Ericsson): tasks just beyond current skill, immediate feedback, repetition of weak spots. Failing tests with clear messages are the feedback; picking the next task from your weak spots is not yet built.
- **Motivation** (Deci and Ryan): autonomy, competence and visible progress sustain effort. The course keeps autonomy (you choose when to open hints) and shows progress; the fear you named, "this is just fill-in-the-blank", is a competence-and-autonomy problem, addressed below.

## 3. Is this better than forking BusTub and porting it yourself?

It can be, in specific ways, and it can fail in others.

**What it removes that teaches nothing:** C++ build setup, translating plumbing (guards, promises, channels), the long wait before you learn that your code is wrong (stage tests are small and answer in seconds), and not knowing what to do next. A fork gives you none of those, and the CMU grader only speaks at the end of a project.

**What a fork gives you that this must not lose:** you design the structures, you meet the ambiguity of the C++ skeleton, you debug a whole system, and you choose how to port each idiom. Measured against that, from the audit:

- Only **10 of 137** task sections invite your own design; **74** say something is "given" (projects 3 and 4 are mostly "fill in the region marked 4a-08"). That is closer to completing a form than to designing a database. Where the lesson is the design (an LRU list, a hash directory, a version chain), more of it should be yours.
- Task text sometimes carried the algorithm (13 stages with numbered recipes). Fixed today: those are now a contract plus a collapsed "steps" aside (see section 6).
- **Prose is thin.** In the 117 concept articles the median is 1,147 words, of which about 309 are prose; about a quarter of the lines are bullets and some articles are mostly tables and code. They read as accurate reference notes, which is useful, but they are not yet the "very high quality prose" you asked for: explanations that start from a problem, build the idea step by step with a worked example, and say how the idea fails. 14 articles ask any question at all.
- **Concept examples are demonstrations, not exercises.** All 117 have tested examples, but you only read them. They need "now you do it" prompts.
- **Ten boss stages** run BusTub's own test with nothing new to write. Fine as a checkpoint, wasteful as learning. Today they got optional experiments.

My verdict: with the contract-style tasks, open questions and experiments in place, the course is better than forking for projects 1 and 2 and for feedback speed, and still weaker than forking for design freedom in projects 3 and 4. Closing that is the main pedagogical task (section 5, step 4).

## 4. What "exercises worth completing" means here

An exercise earns your time when it has a design decision or a debugging step, fails with a message that names the behaviour, has one way of being subtly wrong that a good test finds, and connects to something real (a function in BusTub, RocksDB, Postgres). It fails when a competent reader can finish it by transcribing the text. The audit found three kinds worth keeping (spec-from-behaviour stages like 3g-01, port-and-verify stages like 2b-01, and the concurrency stages with latch hints) and two to reduce (recipe tasks, and stages whose hints give the code line; three of those were rewritten).

## 5. Plan, in the order I recommend

**Update (2026-10-09, later the same day).** The owner decided: the course is restructured around public-API contracts and property tests ([BUSTUB_RESTRUCTURE.md](BUSTUB_RESTRUCTURE.md); module 1a is the pilot), the components stay BusTub's, and what BusTub does not teach (LSM trees, Raft, columnar and vectorised execution, cost-based optimisation, vector and time-series systems) goes to a follow-on course ([ADVANCED_DB_COURSE.md](ADVANCED_DB_COURSE.md)). Recovery stays in BusTub's scope as a new module. Steps 3, 6 and 7 below therefore move: recovery is module 4c; LSM, Raft and the rest are the follow-on course. The prose pilot is done on three articles (`version-chains-and-undo-logs`, `durability-and-fsync`, `unique-indexes-and-tombstone-reuse`); the prose share of those went from about 25 to 80 percent (`tools/concept_prose_report.py`).


**Step 1. Prose pilot (small, do first).** Rewrite three concept articles to the prose rules in the `curriculum-review` skill: one on storage (`slot-allocation-and-invariants`), one on concurrency (`mutex-owns-its-data`) and one on query execution (`window-functions`). Each opens with the problem, builds the idea with one running example, shows the failure, ends with an experiment. Compare time-to-understand with the old versions yourself before we touch the other 114.

**Step 2. Make every concept do something.** Add to each article two retrieval prompts and one kata ("rebuild this in a blank file without looking; here is the test it must pass"). Scripted counts (prose share, questions, katas) join `anneal course lint` as warnings.

**Step 3. Fill the hole BusTub leaves: recovery and logging.** A new module after 4b: write-ahead log, log records, checkpoints, crash injection with a simulated disk (SYSTEMS.md §3.4 `SimDisk`), ARIES-lite redo and undo. This is the part of the interview that BusTub does not cover and the part that most separates database engineers from application engineers.

**Step 4. Restore design freedom where it matters.** For each module in projects 3 and 4, turn the best one or two stages into "design it": the tests use only the public interface, the structure is yours, and the hints discuss alternatives (for example, how to represent an undo log chain). Keep scaffolding for plumbing.

**Step 5. The Rust and systems tracks that are designed but unwritten.** In this order, because each unlocks the next: S6 iterators and S7 smart pointers and interior mutability; L6 closures and L8 error design; C1 threads and shared state, C3 atomics and ordering; K5 files and `fsync`, K7 virtual memory and `mmap`, K16 durability. Every track follows the rules in this document: contract tasks, open design, retrieval prompts, experiments, prose that explains.

**Step 6. Modern storage and execution, as BusTub-style modules.** (a) An LSM tree: memtable, SSTables, bloom filters, compaction, a benchmark against your B+ tree; this is how RocksDB, TiKV, Cassandra and ClickHouse's MergeTree family store data. (b) A small vectorised executor on columnar batches (the model behind Apache Arrow and DataFusion, and the engines built on them). (c) Statistics and cost-based join ordering on top of 3h.

**Step 7. Distributed basics.** A Raft lab (leader election, log replication, a replicated key-value store) in Rust, in the style of MIT 6.5840. Without it, "distributed database" interviews are out of reach.

**Step 8. Evidence a hiring team can see.** One public repository: your BusTub-in-Rust plus the LSM and recovery modules, with benchmarks and a write-up of design decisions and what you measured. Then one contribution to an open-source Rust database project (Apache DataFusion, TiKV, Neon, Materialize, RisingWave and Databend are examples; check which are hiring and welcoming). Add interview practice: explain a system design aloud, whiteboard a B+ tree split, answer "what does `fsync` guarantee" without notes. The mentor skill runs these as gap probes and Feynman checks.

**A rhythm that works for most people** (adjust to your time): three build sessions per week of 90 to 120 minutes on the current stage; one retrieval session of 30 minutes (blank-file rebuild of last week's piece, then two probes); one weekly explain-it session; a monthly benchmark and write-up.

## 6. What changed today, and what is still unverified

Shipped in the working tree: 2,350 stage-test assertions now name the behaviour they check (`tools/add_assert_messages.py`, regenerated template); 13 recipe tasks became a contract plus a collapsed steps aside; 57 missing concept links added as optional reading; 22 open check-yourself questions (no multiple choice); optional experiments on 10 pass-through boss stages; 3 hints that leaked code rewritten; the new standard written into [COURSE_STANDARDS.md](COURSE_STANDARDS.md) §11. `anneal course lint` is clean. `anneal course verify` over all 163 stages was started in the background and had not finished when this was written.

Not done: the prose rewrite, the retrieval prompts and katas, the new modules, and any measurement of whether you learn faster. I cannot judge the last from here.

## 7. How we will know it works

- **Blank-file rebuild rate.** A week after a module, rebuild its core structure from nothing against the tests, with no hints. Track success and time. This is the honest measure of mastery.
- **Time to first hint** and **hints per stage** (the platform can record both; the page already counts hints). If you open hints within two minutes, tasks are too hard or too vague; if never, they may be too easy.
- **Explain-it sessions** scored on a short rubric (accuracy, trade-offs, failure modes).
- **Interview results**: a mock round every month with a person, not me.

## 8. Decisions for you

1. Start with step 1 (prose pilot) or step 3 (recovery module)? I recommend step 1: it is small, it changes how every later module is written, and you can judge it in one sitting.
2. Is the Raft lab in scope, or do you want to stay single-node until the end of 2026?
3. How many hours a week can you give this? The plan above is about 8 to 10.
