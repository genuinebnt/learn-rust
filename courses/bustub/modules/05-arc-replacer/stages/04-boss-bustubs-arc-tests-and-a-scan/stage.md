**Where this fits.** The end of the module: a long run against the model, the experiment that shows what ARC is for, and BusTub's two ARC tests.

> [!CHECK] On the workload of the scan test below, ARC gets a higher hit rate than LRU. Where exactly in the sequence of accesses does the difference arise, and which of ARC's two ideas (the mru/mfu split, the adaptive target) is responsible for it?
> ||It arises in the pages **after each scan**: LRU has pushed out the hot set during the scan and must reload it; ARC kept it on `mfu` because the scan's pages only ever entered `mru` and were evicted from there. The split alone explains it: the target is only needed when the workload *shifts* from recency to frequency and back, which this one does not do much.||
>
> - What is on `mfu` when a scan starts?
> - Which frames does a scan evict?
> - When would the target matter?

## The task

Nothing new to design.

- **A long run.** 30 000 random operations on a pool of 64 frames and 200 pages: every victim and every size equals the model's.
- **A scan.** 24 hot pages are accessed constantly, and every few hundred accesses a scan of 60 never-reused pages goes by. ARC must get a clearly higher hit rate than your LRU replacer from module 1c, in a pool of 32 frames.
- **BusTub's tests.** `arc_replacer_test.rs` (the sample scenario, with its ASCII pictures of the four lists after every step) and `arc_replacer_performance_test.rs` (256 000 frames, hits in the middle of the list, average round under 3 seconds).

## Your freedom

The same as before.

## The Rust toolbox

**Read BusTub's pictures.** The comments in `arc_replacer_test.rs` draw the four lists after each call: `[<-mru_ghost-][<-mru-]![-mfu->][->mfu_ghost->] p=x`. Following the scenario with your own drawing is the best way to check your mental model of ARC.

**Release mode for the performance test.** `cargo test --release --test arc_replacer_performance_test`. A debug build is many times slower and says nothing about your algorithm.

## If this is new

- Everything is in the earlier stages of this module.

## Tests

- 30 000 random operations on 64 frames agree with the model.
- ARC beats LRU on a scan-heavy trace.
- BusTub's `arc_replacer_test` and `arc_replacer_performance_test`.

## Hints

### The sample test fails

The scenario's comments give the expected lists after every call. Print your own lists at the failing call and compare line by line: the first difference is the bug.

### The performance test is slow

A hit in the middle of a list must not walk the list. Where in `record_access` do you search for the frame?

## Performance

Run the scan test with different pool sizes and different scan lengths; at what scan length does LRU's hit rate fall to a fraction of ARC's? Plot hit rate against scan length for both.

## Experiment

Optional. Predict first, then run.

1. **A workload that shifts.** Alternate between a recency-heavy phase (a sliding window of pages) and a frequency-heavy one (a fixed hot set). Print `p` over time (add a debug accessor in your own copy). Does it track the phases?
2. **Compare three.** Put LRU, LRU-2 and ARC through the same scan trace. Which wins, and by how much? What does it say about the cost of ARC's extra bookkeeping?

## Other designs

None for this stage. The *Other designs* sections of 1e-01 to 1e-03 list the alternatives to compare with yours.

## In BusTub

The buffer pool manager in module 1f will use your ARC replacer: `record_access` on every access, `set_evictable(false)` while a page is pinned, `evict` on a miss, `remove` on delete.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `TEST(ArcReplacerTest, SampleTest)` | `#[test] fn sample_test()` |
| `ASSERT_EQ(std::optional<frame_id_t>(2), arc_replacer.Evict())` | `assert_eq!(Some(f(2)), arc_replacer.evict())` |
| `AccessType` argument, ignored by the replacer | omitted |

**Port rule:** an argument the policy ignores can be dropped from the Rust signature.

## Learn more

- [`cargo test --release`](https://doc.rust-lang.org/cargo/commands/cargo-test.html) · Megiddo and Modha, FAST 2003
