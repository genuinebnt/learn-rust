**Where this fits.** The end of the module: check both policies on long runs and in a small simulation of a pool, then run BusTub's two replacer tests.

> [!CHECK] CLOCK is "LRU with one bit". In what situation does it make exactly the same choices as LRU, and in what situation does it differ? What does that tell you about when to trust it as an approximation?
> ||When every use of a frame is a **pin followed by an unpin**, each use takes the frame off the ring and puts it back behind the hand with its bit set, which is the same as moving it to the most recent end of the LRU list; the victim sweep then finds the oldest. The two differ when a frame is unpinned again **without being pinned in between** (CLOCK sets a bit, LRU keeps the old position), so CLOCK only approximates LRU for workloads with many such "touches". Trust it where uses are bursty and exactness costs more than it is worth.||
>
> - What do `pin` and `unpin` do to a frame on the ring?
> - Which operation sets a bit without moving the frame?
> - Where does the hand stand after a long run of victims?

## The task

Nothing new to design. Check that both replacers keep their promises at scale.

- **Long runs.** 20 000 random operations on 300 frames: LRU and CLOCK agree with their models at every step.
- **A pool simulation.** A reference string of 40 000 page accesses (a hot set and a cold set) is replayed through a pool of 32 frames, with each hit as a pin and an unpin. With that usage, CLOCK must choose the **same victims in the same order** as LRU.
- **BusTub's tests.** `tests/lru_replacer_test.rs` and `tests/clock_replacer_test.rs` are `lru_replacer_test.cpp` and the clock equivalent, ported scenario for scenario; `Victim(&frame)` returning a `bool` is `victim()` returning an `Option`.

## Your freedom

The same as before. If a long run fails when the short ones passed, the shrunk counterexample in the earlier stages has a sequence you did not try; a long failing run is an invitation to reduce it by hand to the shortest failing prefix.

## The Rust toolbox

**Read a failing assertion.** The messages here name the step and the two values: `left` is what your code gave, `right` is what the model says. Find the first step that differs, then look at the operation before it.

**Run one test with output.** `cargo test --test stages_1c -- --nocapture s1c_04` prints what the test prints with `eprintln!`, such as the hit rate.

**Release mode.** `cargo test --release` for timing questions. Debug builds are tens of times slower than release, so budget tests should say which they assume.

## If this is new

- Everything is in the earlier stages of this module; the new thing is a long, mixed run, which only asks your code to stay consistent for longer.

## Tests

- 20 000 random operations on 300 frames agree with the models for both policies.
- A cache simulation: CLOCK evicts the same pages as LRU when every hit is a pin then an unpin.
- BusTub's `lru_replacer_test` and `clock_replacer_test`.

## Hints

### The first differing step

Make the failing run smaller by hand: copy the operations that led to the difference into a short test, then remove operations until the difference disappears. What was the last one you could not remove?

### Is it the model or the code?

The models are a few lines each (they are in the test file). Check the one that disagrees with you against the stage page's description of the policy before you change your code.

## Performance

Run the simulation with different pool sizes and see how the hit rate changes. A hit rate of 0.48 at 32 frames means about half of the accesses went to disk: the replacer decides *which* half, but cannot make up for a pool that is too small.

## Experiment

Optional. Predict first, then run.

1. **Change the workload.** Make the cold set bigger than the pool and the hot set smaller than it. Which policy loses more hot pages to a scan? (They are the same here; the next module is where a policy first beats LRU.)
2. **Break the equivalence.** In the simulation, call only `unpin` on a hit (no `pin` first). Predict which policy changes and how, then look at the hit rates.

## Other designs

None for this stage. The *Other designs* sections of 1c-01 to 1c-03 list the alternatives to compare with yours.

## In BusTub

Both replacers are small classes. BusTub's current course replaces them with **LRU-K** (module 1d) and **ARC** (module 1e); these two stay in this course because they are the base case and because CLOCK is what real operating systems use.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `TEST(LRUReplacerTest, SampleTest)` | `#[test] fn sample_test()` |
| `EXPECT_EQ(true, replacer.Victim(&value)); EXPECT_EQ(1, value);` | `assert_eq!(Some(FrameId(1)), replacer.victim());` |
| `ASSERT_EQ(6, replacer.Size());` | `assert_eq!(6, replacer.size());` |

**Port rule:** an out-parameter and a `bool` check become one `Option` comparison.

## Learn more

- [`proptest`](https://docs.rs/proptest) · [the CLOCK page-replacement algorithm](https://en.wikipedia.org/wiki/Page_replacement_algorithm#Clock)
