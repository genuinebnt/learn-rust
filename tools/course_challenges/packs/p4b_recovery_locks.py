from _c import C
M4C, M4D = "22-acid-logging-and-recovery", "23-the-lock-manager"
CH = []

CH.append(C("4c-c1", M4C, "90-challenge-how-much-log-can-go", "build", "Challenge: how much log can go", "easy", "stages_4c::s4c_c1",
  ["finding the oldest log record recovery can still need","three different lower bounds and why all three matter"],
  ["aries-recovery","write-ahead-logging"],
  "`truncation_lsn` in `src/recovery/truncation.rs`: after a checkpoint, the log before some point can be deleted. The point is the **smallest** of three: the checkpoint's own start (analysis begins there), the oldest `rec_lsn` in the dirty page table (redo must start there, for the page that has been dirty longest), and the first log record of the oldest transaction still active (undo may need to walk back to it).",
  "An append-only log that is never truncated fills the disk; a log truncated too eagerly makes recovery impossible, and the error shows only after a crash. The rule is one `min` over three numbers, and the exercise is knowing that it is three, and what each protects.",
  ["`truncation_lsn(checkpoint_begin, dirty_rec_lsns, active_first_lsns)` returns the minimum of `checkpoint_begin`, of every `dirty_rec_lsns` and of every `active_first_lsns`.","With empty lists the answer is `checkpoint_begin`."],
  ["The result is at most each of the three inputs.","The result is one of the inputs."],
  ["Adding a dirty page or an active transaction can only lower (never raise) the result.","The result is monotone in `checkpoint_begin`.","Removing the smallest element of a list raises the result to the next smallest bound."],
  ["checkpoint 100, dirty [90, 120], active [95] -> 90","checkpoint 100, dirty [], active [] -> 100"],
  ["Each bound being the smallest in turn.","Empty lists.","A property against a fold of `min`."],
  src=("src/recovery/truncation.rs", '''
//! How much of the log may be deleted after a checkpoint.

/// The smallest LSN recovery can still need.
pub fn truncation_lsn(checkpoint_begin: u64, dirty_rec_lsns: &[u64], active_first_lsns: &[u64]) -> u64 {
    // @begin 4c-c1
    dirty_rec_lsns.iter().chain(active_first_lsns).copied().fold(checkpoint_begin, u64::min)
    //~ todo!("4c-c1: the smallest of the checkpoint start, the oldest dirty-page record and the oldest active transaction's first record")
    // @end
}
'''),
  test=("tests/stages_4c.rs", '''
use bustub::recovery::truncation::truncation_lsn;

#[test]
fn s4c_c1_each_bound_can_be_the_one_that_matters() {
    assert_eq!(truncation_lsn(100, &[], &[]), 100);
    assert_eq!(truncation_lsn(100, &[90, 120], &[110]), 90, "a page dirty since 90 needs redo from 90");
    assert_eq!(truncation_lsn(100, &[150], &[95]), 95, "an active transaction may need undo back to 95");
    assert_eq!(truncation_lsn(100, &[150], &[180]), 100, "the checkpoint start itself");
}

#[test]
fn s4c_c1_a_checkpoint_at_zero_keeps_everything() {
    assert_eq!(truncation_lsn(0, &[5], &[7]), 0);
}

#[test]
fn s4c_c1_removing_the_oldest_dirty_page_raises_the_bound() {
    assert_eq!(truncation_lsn(100, &[40, 60], &[]), 40);
    assert_eq!(truncation_lsn(100, &[60], &[]), 60);
    assert_eq!(truncation_lsn(100, &[], &[]), 100);
}

#[test]
fn s4c_c1_the_smallest_of_all_three_wins_whatever_the_order_of_the_lists() {
    assert_eq!(truncation_lsn(100, &[70, 90], &[80, 60]), 60);
    assert_eq!(truncation_lsn(100, &[90, 70], &[60, 80]), 60);
    assert_eq!(truncation_lsn(50, &[70, 90], &[80, 60]), 50);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the minimum of all, never above any input, and adding an element only lowers it.
    #[test]
    fn s4c_c1_property_it_is_the_minimum_of_everything(cp in 0u64..100, dirty in proptest::collection::vec(0u64..200, 0..5), active in proptest::collection::vec(0u64..200, 0..5), extra in 0u64..200) {
        let r = truncation_lsn(cp, &dirty, &active);
        prop_assert_eq!(r, dirty.iter().chain(&active).copied().chain(Some(cp)).min().unwrap());
        let mut more = dirty.clone();
        more.push(extra);
        prop_assert!(truncation_lsn(cp, &more, &active) <= r);
        prop_assert!(truncation_lsn(cp + 1, &dirty, &active) >= r);
    }
}
''')))

CH.append(C("4c-c2", M4C, "91-challenge-group-commit", "build", "Challenge: group commit", "medium", "stages_4c::s4c_c2",
  ["acknowledging many commits with one log flush","bounding how long a commit may wait for company"],
  ["write-ahead-logging","durability-and-fsync"],
  "`GroupCommit` in `src/recovery/group_commit.rs`: transactions that want to commit hand their commit record's LSN to `submit(lsn, now)`; the log is flushed for a whole **batch** at once. `poll(now)` returns the batch to acknowledge when the queue has reached `max_batch` or the **oldest** waiting commit has waited `max_wait`; `flush_all()` returns everything waiting.",
  "The expensive part of a commit is the `fsync`, and one `fsync` makes every earlier record durable, whoever wrote it. Batching commits turns a thousand syncs a second into a handful, at the price of a bounded delay for each. The rule is simple and the invariants are what matters: nobody is acknowledged before the flush, nobody is acknowledged twice, nobody waits for ever.",
  ["`submit(lsn, now)` queues the commit (LSNs arrive in increasing order). Time is a number of ticks passed in.","`poll(now)` returns `Some(batch)` (all waiting LSNs, in order) when `queue.len() >= max_batch` or `now - oldest_submit >= max_wait`, and `None` otherwise; the batch leaves the queue.","`flush_all()` returns whatever waits (possibly nothing) and empties the queue. `pending()` is the queue length."],
  ["Every submitted LSN is returned in exactly one batch, in submission order.","A batch is never returned while neither condition holds.","`pending()` is submissions minus acknowledgements."],
  ["No commit waits longer than `max_wait` once `poll` is called at that time.","A batch never has fewer than 1 element.","Polling twice at the same time returns a batch at most once (the second poll finds the queue empty or below the threshold)."],
  ["max_batch 3, max_wait 10: submit 1@0, 2@1: poll@2 -> None; submit 3@2: poll@2 -> [1,2,3]; submit 4@5: poll@16 -> [4]"],
  ["Batch-size trigger, time trigger, neither.","`flush_all`.","A property: everything acknowledged once and in order."],
  src=("src/recovery/group_commit.rs", '''
//! Batching commit acknowledgements behind one log flush.

use std::collections::VecDeque;

pub struct GroupCommit {
    // @begin 4c-c2
    max_batch: usize,
    max_wait: u64,
    /// (lsn, submitted at), oldest first.
    queue: VecDeque<(u64, u64)>,
    //~ _gc: (),
    // @end
}

impl GroupCommit {
    pub fn new(max_batch: usize, max_wait: u64) -> GroupCommit {
        // @begin 4c-c2
        GroupCommit { max_batch: max_batch.max(1), max_wait, queue: VecDeque::new() }
        //~ todo!("4c-c2: an empty queue with the two limits")
        // @end
    }

    pub fn submit(&mut self, lsn: u64, now: u64) {
        // @begin 4c-c2
        self.queue.push_back((lsn, now));
        //~ todo!("4c-c2: queue the commit with the time it arrived")
        // @end
    }

    pub fn poll(&mut self, now: u64) -> Option<Vec<u64>> {
        // @begin 4c-c2
        let (_, oldest) = *self.queue.front()?;
        if self.queue.len() >= self.max_batch || now.saturating_sub(oldest) >= self.max_wait {
            Some(self.queue.drain(..).map(|(l, _)| l).collect())
        } else {
            None
        }
        //~ todo!("4c-c2: a batch when the queue is full enough or the oldest has waited long enough")
        // @end
    }

    pub fn flush_all(&mut self) -> Vec<u64> {
        // @begin 4c-c2
        self.queue.drain(..).map(|(l, _)| l).collect()
        //~ todo!("4c-c2: everything that waits")
        // @end
    }

    pub fn pending(&self) -> usize {
        // @begin 4c-c2
        self.queue.len()
        //~ todo!("4c-c2: how many commits wait")
        // @end
    }
}
'''),
  test=("tests/stages_4c.rs", '''
use bustub::recovery::group_commit::GroupCommit;

#[test]
fn s4c_c2_a_full_queue_is_flushed_at_once() {
    let mut g = GroupCommit::new(3, 10);
    g.submit(1, 0);
    g.submit(2, 1);
    assert_eq!(g.poll(2), None);
    g.submit(3, 2);
    assert_eq!(g.poll(2), Some(vec![1, 2, 3]));
    assert_eq!(g.pending(), 0);
}

#[test]
fn s4c_c2_the_oldest_commit_never_waits_longer_than_the_limit() {
    let mut g = GroupCommit::new(10, 10);
    g.submit(4, 5);
    assert_eq!(g.poll(14), None);
    assert_eq!(g.poll(15), Some(vec![4]));
}

#[test]
fn s4c_c2_a_newer_commit_rides_with_an_older_one_that_timed_out() {
    let mut g = GroupCommit::new(10, 10);
    g.submit(1, 0);
    g.submit(2, 9);
    assert_eq!(g.poll(10), Some(vec![1, 2]), "the oldest has waited 10: the whole queue goes");
}

#[test]
fn s4c_c2_polling_an_empty_queue_and_polling_twice() {
    let mut g = GroupCommit::new(2, 5);
    assert_eq!(g.poll(100), None);
    g.submit(1, 0);
    g.submit(2, 0);
    assert!(g.poll(0).is_some());
    assert_eq!(g.poll(0), None);
}

#[test]
fn s4c_c2_flush_all_returns_everything_in_order() {
    let mut g = GroupCommit::new(100, 100);
    for l in [5, 6, 7] {
        g.submit(l, 0);
    }
    assert_eq!(g.flush_all(), vec![5, 6, 7]);
    assert_eq!(g.flush_all(), Vec::<u64>::new());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: every submission is acknowledged exactly once and in order, and only when a trigger held.
    #[test]
    fn s4c_c2_property_everything_is_acknowledged_once_in_order(max_batch in 1usize..5, max_wait in 0u64..8, steps in proptest::collection::vec((0u64..4, 0u8..3), 0..40)) {
        let mut g = GroupCommit::new(max_batch, max_wait);
        let (mut now, mut next_lsn) = (0u64, 1u64);
        let mut submitted: Vec<(u64, u64)> = Vec::new();
        let mut acked: Vec<u64> = Vec::new();
        for (dt, op) in steps {
            now += dt;
            if op < 2 {
                g.submit(next_lsn, now);
                submitted.push((next_lsn, now));
                next_lsn += 1;
            }
            if let Some(batch) = g.poll(now) {
                let waiting = &submitted[acked.len()..];
                prop_assert!(!batch.is_empty());
                prop_assert!(waiting.len() >= max_batch || now - waiting[0].1 >= max_wait, "flushed with no trigger");
                acked.extend(batch);
            }
            prop_assert_eq!(g.pending(), submitted.len() - acked.len());
        }
        acked.extend(g.flush_all());
        prop_assert_eq!(acked, submitted.iter().map(|s| s.0).collect::<Vec<_>>());
    }
}
''')))

CH.append(C("4c-c3", M4C, "92-challenge-redo-that-goes-backwards", "debug", "Challenge: redo that goes backwards", "easy", "stages_4c::s4c_c3",
  ["finding the rule that makes redo idempotent: compare record LSN with page LSN"],
  ["aries-recovery","write-ahead-logging","property-testing-and-fuzzing"],
  "`redo` in `src/recovery/redo_pass.rs` replays log records onto pages after a crash. Each page remembers the LSN of the last record applied to it (`page_lsn`). It looks right, and on a page that had already been flushed with newer changes, recovery writes an **older** value back over it. Find the bug and fix it.",
  "Redo must be **idempotent**: replaying the whole log from the start gives the same result as replaying only what the disk is missing, because recovery cannot know which pages were flushed before the crash. The page LSN is how: apply a record only if the page has not seen it yet. Skip the check and recovery undoes work the disk already had.",
  ["`redo(pages, log)`: `pages[p]` is `(page_lsn, value)`; each record is `(lsn, page, new value)` in increasing LSN order.","A record is applied iff `lsn > page_lsn`; applying sets the value and `page_lsn = lsn`."],
  ["A page's `page_lsn` never decreases.","After redo, every page's value is the value of the record with the highest LSN for it that is at least its previous `page_lsn` (or its original value)."],
  ["Running `redo` twice gives the same pages as running it once.","Starting from pages that already reflect a prefix of the log gives the same result as starting from empty pages.","Records already reflected are skipped, and nothing is applied out of order."],
  ["page 0 = (5, 'new'); log [(3, 0, 'old'), (7, 0, 'newer')] -> (7, 'newer'), and 'old' is never written"],
  ["A page ahead of the log.","Repeated redo.","A property: any prefix already applied gives the same final state."],
  src=("src/recovery/redo_pass.rs", '''
//! The redo pass of recovery over simple pages.

/// `pages[i] = (page_lsn, value)`; `log` is `(lsn, page, value)` in increasing LSN order.
pub fn redo(pages: &mut [(u64, i64)], log: &[(u64, usize, i64)]) {
    for &(lsn, page, value) in log {
        // @begin 4c-c3
        if lsn > pages[page].0 {
            pages[page] = (lsn, value);
        }
        //~ pages[page] = (lsn, value);
        // @end
    }
}
'''),
  test=("tests/stages_4c.rs", '''
use bustub::recovery::redo_pass::redo;

#[test]
fn s4c_c3_a_page_that_is_ahead_of_a_record_is_left_alone() {
    let mut pages = vec![(5, 100)];
    redo(&mut pages, &[(3, 0, 1), (7, 0, 2)]);
    assert_eq!(pages, vec![(7, 2)]);
}

#[test]
fn s4c_c3_redo_twice_is_the_same_as_once() {
    let log = [(1, 0, 10), (2, 1, 20), (3, 0, 30)];
    let mut once = vec![(0, 0), (0, 0)];
    redo(&mut once, &log);
    let mut twice = once.clone();
    redo(&mut twice, &log);
    assert_eq!(once, twice);
    assert_eq!(once, vec![(3, 30), (2, 20)]);
}

#[test]
fn s4c_c3_a_page_flushed_at_the_record_is_not_applied_again() {
    let mut pages = vec![(4, 40)];
    redo(&mut pages, &[(4, 0, 999)]);
    assert_eq!(pages, vec![(4, 40)], "the same LSN has already been applied");
}

#[test]
fn s4c_c3_unrelated_pages_are_independent() {
    let mut pages = vec![(10, 1), (0, 0)];
    redo(&mut pages, &[(2, 0, 7), (3, 1, 8)]);
    assert_eq!(pages, vec![(10, 1), (3, 8)]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: starting from pages that already reflect a prefix of the log gives the same result as redoing the whole log from empty pages.
    #[test]
    fn s4c_c3_property_a_prefix_already_applied_changes_nothing(recs in proptest::collection::vec((0usize..3, -9i64..9), 0..20), cut in 0usize..21) {
        let log: Vec<(u64, usize, i64)> = recs.iter().enumerate().map(|(i, &(p, v))| (i as u64 + 1, p, v)).collect();
        let mut full = vec![(0u64, 0i64); 3];
        redo(&mut full, &log);
        let cut = cut.min(log.len());
        let mut partial = vec![(0u64, 0i64); 3];
        redo(&mut partial, &log[..cut]);
        redo(&mut partial, &log);
        prop_assert_eq!(&partial, &full);
        let before = full.clone();
        redo(&mut full, &log);
        prop_assert_eq!(full, before);
    }
}
''')))

CH.append(C("4c-c4", M4C, "93-challenge-point-in-time-recovery", "build", "Challenge: point-in-time recovery", "medium", "stages_4c::s4c_c4",
  ["replaying a log only up to a chosen point, applying only committed transactions","what 'as of LSN n' means for a transaction that committed after n"],
  ["aries-recovery","write-ahead-logging"],
  "`recover_until` in `src/recovery/pitr.rs`: given a log of `Begin`, `Set(txn, key, value)`, `Commit` and `Abort` records (each with an increasing LSN), rebuild the database **as of** `upto_lsn`: the effect of every transaction whose `Commit` record has `lsn <= upto_lsn`, applied in log order. Transactions that had not committed by then (still running, aborted, or committed later) have no effect.",
  "\"Restore the database to just before the bad `DROP TABLE`\" is point-in-time recovery, and it is nothing more than recovery that stops early. The base backup plus the log up to a chosen LSN gives the state at that moment; the one subtle point is that a transaction either committed at or before the point, and counts completely, or it does not count at all.",
  ["`recover_until(log, upto_lsn)` returns the key-value map.","A transaction's `Set` records take effect, in LSN order among all committed transactions, iff its `Commit` is in the log at an LSN `<= upto_lsn`.","Records after `upto_lsn` are ignored. A transaction with `Abort`, or with no outcome by `upto_lsn`, has no effect."],
  ["The result depends only on the records with `lsn <= upto_lsn`.","Every key in the result was set by a transaction committed by `upto_lsn`."],
  ["`recover_until(log, a)` followed by the committed effects between `a` and `b` equals `recover_until(log, b)`.","Raising `upto_lsn` past the end of the log gives the full recovery.","An aborted transaction never appears, at any `upto_lsn`."],
  ["log: B1 S1(k=1) C1@4 B2 S2(k=1,v=2) C2@8: recover_until(5) -> {k: 1}; recover_until(9) -> {k: 2}"],
  ["Commits before and after the point.","Aborted and unfinished transactions.","A property: monotone extension and equality at the end."],
  src=("src/recovery/pitr.rs", '''
//! Recovering the database as of a log position.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Rec {
    Begin(u32),
    Set(u32, i64, i64),
    Commit(u32),
    Abort(u32),
}

/// `log` is `(lsn, record)` in increasing LSN order.
pub fn recover_until(log: &[(u64, Rec)], upto_lsn: u64) -> BTreeMap<i64, i64> {
    // @begin 4c-c4
    let committed: BTreeSet<u32> = log.iter().filter(|(lsn, _)| *lsn <= upto_lsn).filter_map(|(_, r)| if let Rec::Commit(t) = r { Some(*t) } else { None }).collect();
    let mut db = BTreeMap::new();
    for (lsn, rec) in log {
        if *lsn > upto_lsn {
            break;
        }
        if let Rec::Set(t, k, v) = rec {
            if committed.contains(t) {
                db.insert(*k, *v);
            }
        }
    }
    db
    //~ todo!("4c-c4: find the transactions committed by the point; apply only their writes, in log order")
    // @end
}
'''),
  test=("tests/stages_4c.rs", '''
use bustub::recovery::pitr::{recover_until, Rec::*};
use std::collections::BTreeMap;

fn log() -> Vec<(u64, bustub::recovery::pitr::Rec)> {
    vec![(1, Begin(1)), (2, Set(1, 7, 1)), (4, Commit(1)), (5, Begin(2)), (6, Set(2, 7, 2)), (7, Set(2, 8, 5)), (8, Commit(2))]
}

#[test]
fn s4c_c4_a_commit_after_the_point_does_not_count() {
    assert_eq!(recover_until(&log(), 5), BTreeMap::from([(7, 1)]));
    assert_eq!(recover_until(&log(), 7), BTreeMap::from([(7, 1)]), "writes of an uncommitted transaction are not applied");
}

#[test]
fn s4c_c4_the_whole_log_gives_the_full_recovery() {
    assert_eq!(recover_until(&log(), 8), BTreeMap::from([(7, 2), (8, 5)]));
    assert_eq!(recover_until(&log(), u64::MAX), BTreeMap::from([(7, 2), (8, 5)]));
}

#[test]
fn s4c_c4_before_the_first_commit_nothing_is_there() {
    assert_eq!(recover_until(&log(), 3), BTreeMap::new());
    assert_eq!(recover_until(&[], 100), BTreeMap::new());
}

#[test]
fn s4c_c4_aborted_transactions_never_appear() {
    let l = vec![(1, Begin(1)), (2, Set(1, 1, 1)), (3, Abort(1)), (4, Begin(2)), (5, Set(2, 2, 2)), (6, Commit(2))];
    assert_eq!(recover_until(&l, 100), BTreeMap::from([(2, 2)]));
}

#[test]
fn s4c_c4_interleaved_transactions_apply_in_log_order() {
    let l = vec![(1, Set(2, 5, 20)), (2, Set(1, 5, 10)), (3, Commit(1)), (4, Commit(2))];
    assert_eq!(recover_until(&l, 100), BTreeMap::from([(5, 10)]), "the writes are applied in log order: transaction 1 wrote last, though transaction 2 committed last");
    assert_eq!(recover_until(&l, 3), BTreeMap::from([(5, 10)]));
    assert_eq!(recover_until(&l, 2), BTreeMap::new());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the state as of a point equals recovering a log cut at that point, and raising the point only adds committed transactions.
    #[test]
    fn s4c_c4_property_recovery_depends_only_on_the_prefix(events in proptest::collection::vec((0u32..3, 0u8..4, 0i64..3, 0i64..9), 0..20), cut in 0u64..25) {
        let mut log = Vec::new();
        let mut finished = std::collections::BTreeSet::new();
        for (i, (t, kind, k, v)) in events.into_iter().enumerate() {
            let lsn = i as u64 + 1;
            if finished.contains(&t) { continue; }
            match kind {
                0 | 1 => log.push((lsn, Set(t, k, v))),
                2 => { log.push((lsn, Commit(t))); finished.insert(t); }
                _ => { log.push((lsn, Abort(t))); finished.insert(t); }
            }
        }
        let prefix: Vec<_> = log.iter().filter(|(l, _)| *l <= cut).cloned().collect();
        prop_assert_eq!(recover_until(&log, cut), recover_until(&prefix, cut));
        prop_assert_eq!(recover_until(&log, 1000), recover_until(&log, u64::MAX));
    }
}
''')))

CH.append(C("4c-c5", M4C, "94-challenge-the-analysis-pass", "build", "Challenge: the analysis pass", "medium", "stages_4c::s4c_c5",
  ["rebuilding the active-transaction table and the dirty-page table from a checkpoint and the log after it","what each record type changes"],
  ["aries-recovery","write-ahead-logging","checking-invariants"],
  "`analyze` in `src/recovery/analysis.rs`: the first pass of ARIES-style recovery. Starting from the state recorded in the last **checkpoint** (the active transactions and the dirty page table at that moment) and scanning the log records after it, rebuild what was true at the crash: which transactions were still active (their work must be undone) and which pages were possibly dirty, with the LSN of the first record that dirtied each (where redo must start).",
  "Recovery cannot trust anything in memory; it has the log. Analysis is the cheap pass that reads the log tail once and produces the two tables the redo and undo passes run from. It is also the pass most easily broken by a missing case: a transaction that began after the checkpoint, one that ended after it, a page dirtied again after being dirtied before.",
  ["Records: `Begin(txn)`, `Update(txn, page)`, `Commit(txn)`, `Abort(txn)` (an abort finished its rollback and ends the transaction).","Start with `checkpoint.active` and `checkpoint.dirty` (page -> rec_lsn). `Begin` adds the transaction. `Update` adds the transaction if unknown and records `page -> lsn` if the page is **not already** in the dirty table. `Commit` and `Abort` remove the transaction.","`analyze(checkpoint, records_after)` returns `Analysis { active, dirty }`."],
  ["`dirty[page]` is always the LSN of the first update that dirtied it since it was last known clean (the checkpoint's value if present).","A committed or aborted transaction is not in `active`."],
  ["Analyzing the whole log from an empty checkpoint equals analyzing a suffix from the checkpoint taken at its start.","Appending a `Commit` removes exactly one transaction and leaves `dirty` unchanged.","Re-dirtying a page never changes its rec_lsn."],
  ["checkpoint: active {1}, dirty {A: 10}; records: Update(1,A)@12, Begin(2)@13, Update(2,B)@14, Commit(1)@15 -> active {2}, dirty {A: 10, B: 14}"],
  ["Each record type; checkpoint state carried over.","Unknown transactions that appear in updates.","A property against replaying the whole log."],
  src=("src/recovery/analysis.rs", '''
//! The analysis pass of recovery.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LogRec {
    Begin(u32),
    Update(u32, u32),
    Commit(u32),
    Abort(u32),
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Analysis {
    pub active: BTreeSet<u32>,
    /// page -> the LSN of the first record that dirtied it
    pub dirty: BTreeMap<u32, u64>,
}

/// `checkpoint` is the state recorded by the last checkpoint; `after` are `(lsn, record)` pairs in log order.
pub fn analyze(checkpoint: &Analysis, after: &[(u64, LogRec)]) -> Analysis {
    // @begin 4c-c5
    let mut a = checkpoint.clone();
    for (lsn, rec) in after {
        match rec {
            LogRec::Begin(t) => {
                a.active.insert(*t);
            }
            LogRec::Update(t, page) => {
                a.active.insert(*t);
                a.dirty.entry(*page).or_insert(*lsn);
            }
            LogRec::Commit(t) | LogRec::Abort(t) => {
                a.active.remove(t);
            }
        }
    }
    a
    //~ todo!("4c-c5: start from the checkpoint and let each record change the two tables")
    // @end
}
'''),
  test=("tests/stages_4c.rs", '''
use bustub::recovery::analysis::{analyze, Analysis, LogRec::*};
use std::collections::{BTreeMap, BTreeSet};

fn a(active: &[u32], dirty: &[(u32, u64)]) -> Analysis {
    Analysis { active: active.iter().copied().collect::<BTreeSet<_>>(), dirty: dirty.iter().copied().collect::<BTreeMap<_, _>>() }
}

#[test]
fn s4c_c5_the_checkpoint_state_is_carried_forward() {
    let cp = a(&[1], &[(0, 10)]);
    let after = vec![(12, Update(1, 0)), (13, Begin(2)), (14, Update(2, 5)), (15, Commit(1))];
    assert_eq!(analyze(&cp, &after), a(&[2], &[(0, 10), (5, 14)]));
}

#[test]
fn s4c_c5_a_page_keeps_the_lsn_of_its_first_dirtying() {
    let after = vec![(1, Update(1, 7)), (2, Update(1, 7)), (3, Update(2, 7))];
    assert_eq!(analyze(&Analysis::default(), &after).dirty, BTreeMap::from([(7, 1)]));
}

#[test]
fn s4c_c5_a_transaction_first_seen_in_an_update_is_active() {
    let after = vec![(5, Update(9, 1))];
    assert_eq!(analyze(&Analysis::default(), &after).active, BTreeSet::from([9]));
}

#[test]
fn s4c_c5_commit_and_abort_both_end_a_transaction() {
    let after = vec![(1, Begin(1)), (2, Begin(2)), (3, Commit(1)), (4, Abort(2))];
    assert_eq!(analyze(&Analysis::default(), &after).active, BTreeSet::new());
}

#[test]
fn s4c_c5_no_records_after_the_checkpoint_gives_the_checkpoint() {
    let cp = a(&[3], &[(1, 2)]);
    assert_eq!(analyze(&cp, &[]), cp);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: analysing a whole log equals analysing the part after a checkpoint taken in the middle of it.
    #[test]
    fn s4c_c5_property_a_checkpoint_in_the_middle_changes_nothing(events in proptest::collection::vec((0u8..4, 0u32..3, 0u32..3), 0..20), cut in 0usize..21) {
        let log: Vec<(u64, bustub::recovery::analysis::LogRec)> = events.iter().enumerate().map(|(i, &(k, t, p))| (i as u64 + 1, match k { 0 => Begin(t), 1 | 2 => Update(t, p), _ => Commit(t) })).collect();
        let cut = cut.min(log.len());
        let whole = analyze(&Analysis::default(), &log);
        let checkpoint = analyze(&Analysis::default(), &log[..cut]);
        prop_assert_eq!(analyze(&checkpoint, &log[cut..]), whole);
    }
}
''')))

CH.append(C("4d-c1", M4D, "90-challenge-wait-die-and-wound-wait", "build", "Challenge: wait-die and wound-wait", "easy", "stages_4d::s4d_c1",
  ["preventing deadlock by comparing ages at request time","the two policies are mirror images"],
  ["waits-for-graphs-and-deadlock-detection","deadlock-and-lock-ordering"],
  "`decide` in `src/concurrency/deadlock_prevention.rs`: when a transaction `requester` asks for a lock held by `holder`, a prevention policy decides at once what happens, using the two start timestamps (smaller = older). **Wait-die**: an older requester **waits**, a younger one **dies** (aborts itself). **Wound-wait**: an older requester **wounds** the holder (the holder is aborted), a younger one **waits**.",
  "Detection finds deadlocks after they happen; prevention makes them impossible by never letting a younger transaction be waited for by an older one (wait-die) or an older one wait for a younger one (wound-wait). No graph, no detector thread; the cost is some aborts that detection would not have needed. Both rules fit in one match, and the property that they never form a cycle is the point.",
  ["`decide(policy, requester_ts, holder_ts) -> Decision`, `Decision` is `Wait`, `AbortRequester` or `AbortHolder`.","Timestamps are distinct; smaller means older.","`WaitDie`: older requester waits, younger aborts itself. `WoundWait`: older requester aborts the holder, younger waits."],
  ["Under each policy, a transaction only ever waits for transactions of one age relation (younger for wait-die, older for wound-wait).","The decision depends only on the order of the two timestamps."],
  ["A waits-for graph built only from `Wait` decisions never has a cycle.","Swapping the roles of the two policies mirrors the decisions.","The oldest transaction is never aborted by the wait-die rule and always wins under wound-wait."],
  ["wait-die: requester 5, holder 9 (older asks) -> Wait; requester 9, holder 5 -> AbortRequester","wound-wait: requester 5, holder 9 -> AbortHolder; requester 9, holder 5 -> Wait"],
  ["Each policy and each age order.","A simulation: no cycle in the waits-for graph.","A property over random timestamps."],
  src=("src/concurrency/deadlock_prevention.rs", '''
//! Deadlock prevention by age.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Policy {
    WaitDie,
    WoundWait,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Decision {
    Wait,
    AbortRequester,
    AbortHolder,
}

/// A smaller timestamp is an older transaction.
pub fn decide(policy: Policy, requester_ts: u64, holder_ts: u64) -> Decision {
    // @begin 4d-c1
    let requester_is_older = requester_ts < holder_ts;
    match (policy, requester_is_older) {
        (Policy::WaitDie, true) => Decision::Wait,
        (Policy::WaitDie, false) => Decision::AbortRequester,
        (Policy::WoundWait, true) => Decision::AbortHolder,
        (Policy::WoundWait, false) => Decision::Wait,
    }
    //~ todo!("4d-c1: compare the ages and apply the policy")
    // @end
}
'''),
  test=("tests/stages_4d.rs", '''
use bustub::concurrency::deadlock_prevention::{decide, Decision::*, Policy::*};

#[test]
fn s4d_c1_wait_die() {
    assert_eq!(decide(WaitDie, 5, 9), Wait, "an older transaction may wait for a younger one");
    assert_eq!(decide(WaitDie, 9, 5), AbortRequester, "a younger one dies rather than wait for an older one");
}

#[test]
fn s4d_c1_wound_wait() {
    assert_eq!(decide(WoundWait, 5, 9), AbortHolder, "an older transaction wounds a younger holder");
    assert_eq!(decide(WoundWait, 9, 5), Wait, "a younger one waits for an older one");
}

#[test]
fn s4d_c1_the_decision_depends_only_on_the_order() {
    for p in [WaitDie, WoundWait] {
        assert_eq!(decide(p, 1, 2), decide(p, 100, 200));
        assert_eq!(decide(p, 2, 1), decide(p, 200, 100));
    }
}

#[test]
fn s4d_c1_swapping_the_two_transactions_swaps_who_gives_way() {
    for (a, b) in [(1, 2), (10, 11), (3, 400)] {
        assert_eq!((decide(WaitDie, a, b), decide(WaitDie, b, a)), (Wait, AbortRequester));
        assert_eq!((decide(WoundWait, a, b), decide(WoundWait, b, a)), (AbortHolder, Wait));
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: under either policy the waits-for graph built from Wait decisions is acyclic, for any pattern of requests.
    #[test]
    fn s4d_c1_property_waiting_never_forms_a_cycle(requests in proptest::collection::vec((0u64..6, 0u64..6), 0..30)) {
        for policy in [WaitDie, WoundWait] {
            let mut edges: Vec<(u64, u64)> = Vec::new();
            for &(req, holder) in &requests {
                if req == holder { continue; }
                if decide(policy, req, holder) == Wait { edges.push((req, holder)); }
            }
            // a cycle would need an edge that goes "against" the age order; under each policy all waits go one way
            for &(a, b) in &edges {
                match policy { WaitDie => prop_assert!(a < b), WoundWait => prop_assert!(a > b) }
            }
            // and so no path can return to its start
            let mut reach: Vec<Vec<u64>> = vec![Vec::new(); 6];
            for &(a, b) in &edges { reach[a as usize].push(b); }
            for start in 0..6u64 {
                let mut seen = std::collections::HashSet::new();
                let mut stack: Vec<u64> = reach[start as usize].clone();
                while let Some(x) = stack.pop() {
                    prop_assert!(x != start, "a cycle through {} under {:?}", start, policy);
                    if seen.insert(x) { stack.extend(reach[x as usize].iter().copied()); }
                }
            }
        }
    }
}
''')))

CH.append(C("4d-c2", M4D, "91-challenge-range-locks", "build", "Challenge: range locks", "medium", "stages_4d::s4d_c2",
  ["locking a range of keys, not just the keys that exist","overlap of half-open ranges and shared/exclusive compatibility"],
  ["lock-modes-and-two-phase-locking","serializable-validation-by-predicates"],
  "`RangeLocks` in `src/concurrency/range_locks.rs`: a table of locks on **half-open key ranges** `[lo, hi)` in `Shared` or `Exclusive` mode. `try_lock(txn, lo, hi, mode)` grants the lock unless another transaction holds an **overlapping** range in an incompatible mode (shared with shared is fine); `unlock_all(txn)` frees everything a transaction holds.",
  "A row lock cannot stop a *phantom*: a scan of `age BETWEEN 30 AND 40` under row locks does not prevent another transaction from inserting age 35. Locking the **range** does, including the keys that do not exist yet. This is the idea behind next-key locks in InnoDB and gap locks everywhere, reduced to its core: intervals and compatibility.",
  ["Ranges are `[lo, hi)`; an empty range (`lo >= hi`) is refused with `Err(EmptyRange)`.","Two ranges overlap iff `a.lo < b.hi && b.lo < a.hi`. A request conflicts with a lock of **another** transaction that overlaps and is not Shared-vs-Shared.","`try_lock` returns `Ok(true)` (granted), `Ok(false)` (conflict, nothing changes). A transaction never conflicts with its own locks."],
  ["Granted locks of different transactions never overlap in an incompatible way.","`unlock_all` removes exactly that transaction's locks."],
  ["Shrinking a requested range never turns a grant into a refusal.","Two shared requests are granted regardless of overlap; an exclusive request overlapping any other transaction's lock is refused.","Adjacent ranges `[0,5)` and `[5,9)` do not overlap."],
  ["T1 S[0,10); T2 S[5,15) ok; T3 X[9,12) refused; T3 X[10,12) refused (T2 holds up to 15); unlock T2; T3 X[10,12) ok"],
  ["Overlap and adjacency.","Compatible and incompatible modes.","Own locks.","A property against a brute-force point check."],
  src=("src/concurrency/range_locks.rs", '''
//! Locks on half-open key ranges.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Shared,
    Exclusive,
}

#[derive(Debug, PartialEq, Eq)]
pub struct EmptyRange;

#[derive(Default)]
pub struct RangeLocks {
    // @begin 4d-c2
    held: Vec<(u32, i64, i64, Mode)>,
    //~ _rl: (),
    // @end
}

impl RangeLocks {
    pub fn new() -> RangeLocks {
        // @begin 4d-c2
        RangeLocks { held: Vec::new() }
        //~ todo!("4d-c2: no locks held")
        // @end
    }

    pub fn try_lock(&mut self, txn: u32, lo: i64, hi: i64, mode: Mode) -> Result<bool, EmptyRange> {
        // @begin 4d-c2
        if lo >= hi {
            return Err(EmptyRange);
        }
        let conflict = self.held.iter().any(|&(t, l, h, m)| t != txn && lo < h && l < hi && !(m == Mode::Shared && mode == Mode::Shared));
        if conflict {
            return Ok(false);
        }
        self.held.push((txn, lo, hi, mode));
        Ok(true)
        //~ todo!("4d-c2: refuse on an overlapping incompatible lock of another transaction; otherwise record it")
        // @end
    }

    pub fn unlock_all(&mut self, txn: u32) -> usize {
        // @begin 4d-c2
        let before = self.held.len();
        self.held.retain(|h| h.0 != txn);
        before - self.held.len()
        //~ todo!("4d-c2: drop the transaction's locks")
        // @end
    }

    pub fn held_by(&self, txn: u32) -> usize {
        // @begin 4d-c2
        self.held.iter().filter(|h| h.0 == txn).count()
        //~ todo!("4d-c2: how many locks the transaction holds")
        // @end
    }
}
'''),
  test=("tests/stages_4d.rs", '''
use bustub::concurrency::range_locks::{EmptyRange, Mode::*, RangeLocks};

#[test]
fn s4d_c2_shared_ranges_overlap_freely_and_exclusive_ones_do_not() {
    let mut l = RangeLocks::new();
    assert_eq!(l.try_lock(1, 0, 10, Shared), Ok(true));
    assert_eq!(l.try_lock(2, 5, 15, Shared), Ok(true));
    assert_eq!(l.try_lock(3, 9, 12, Exclusive), Ok(false));
    assert_eq!(l.try_lock(3, 20, 30, Exclusive), Ok(true));
}

#[test]
fn s4d_c2_a_phantom_insert_is_a_conflict_with_the_range_not_a_row() {
    let mut l = RangeLocks::new();
    l.try_lock(1, 30, 41, Shared).unwrap();
    assert_eq!(l.try_lock(2, 35, 36, Exclusive), Ok(false), "inserting 35 would change what the scan returns");
    assert_eq!(l.try_lock(2, 41, 42, Exclusive), Ok(true));
}

#[test]
fn s4d_c2_adjacent_ranges_do_not_overlap() {
    let mut l = RangeLocks::new();
    l.try_lock(1, 0, 5, Exclusive).unwrap();
    assert_eq!(l.try_lock(2, 5, 9, Exclusive), Ok(true));
    assert_eq!(l.try_lock(3, 4, 6, Shared), Ok(false));
}

#[test]
fn s4d_c2_a_transaction_does_not_conflict_with_itself_and_unlock_frees_the_range() {
    let mut l = RangeLocks::new();
    assert_eq!(l.try_lock(1, 0, 10, Exclusive), Ok(true));
    assert_eq!(l.try_lock(1, 5, 15, Exclusive), Ok(true));
    assert_eq!(l.held_by(1), 2);
    assert_eq!(l.try_lock(2, 12, 13, Shared), Ok(false));
    assert_eq!(l.unlock_all(1), 2);
    assert_eq!(l.try_lock(2, 12, 13, Shared), Ok(true));
}

#[test]
fn s4d_c2_empty_ranges_are_refused() {
    let mut l = RangeLocks::new();
    assert_eq!(l.try_lock(1, 5, 5, Shared), Err(EmptyRange));
    assert_eq!(l.try_lock(1, 7, 3, Exclusive), Err(EmptyRange));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a per-key brute force: a request conflicts iff some key in it is covered by another transaction's incompatible lock.
    #[test]
    fn s4d_c2_property_ranges_match_a_per_key_check(ops in proptest::collection::vec((1u32..4, 0i64..12, 1i64..6, any::<bool>()), 0..25)) {
        let mut l = RangeLocks::new();
        let mut model: Vec<(u32, i64, i64, bool)> = Vec::new(); // (txn, lo, hi, exclusive)
        for (txn, lo, len, excl) in ops {
            let hi = lo + len;
            let conflict = model.iter().any(|&(t, a, b, e)| t != txn && (lo..hi).any(|k| (a..b).contains(&k)) && (e || excl));
            let got = l.try_lock(txn, lo, hi, if excl { Exclusive } else { Shared }).unwrap();
            prop_assert_eq!(got, !conflict);
            if got { model.push((txn, lo, hi, excl)); }
        }
    }
}
''')))

CH.append(C("4d-c3", M4D, "92-challenge-choosing-the-victim", "build", "Challenge: choosing the victim", "easy", "stages_4d::s4d_c3",
  ["policies for which transaction in a deadlock cycle to abort","deterministic tie-breaking"],
  ["waits-for-graphs-and-deadlock-detection"],
  "`choose_victim` in `src/concurrency/victim.rs`: given the transactions on a deadlock cycle, each with its id, its start timestamp, the number of locks it holds and the amount of work it has done, pick the one to abort under a policy: `Youngest` (the latest start), `FewestLocks`, or `LeastWork`. **Ties are broken by the larger id** (the newer transaction).",
  "Every cycle needs a victim, and the choice is a trade-off: the youngest has probably done the least, the one with the fewest locks disturbs the fewest others, the one with the least work wastes the least. Whatever the policy, the choice must be deterministic and must eventually let an old transaction finish (a victim that restarts with a *new* timestamp can starve; keeping the original start prevents it).",
  ["`choose_victim(policy, cycle)` returns the index into `cycle` of the victim; `None` for an empty cycle.","`Youngest`: the largest `start_ts`. `FewestLocks`: the smallest `locks`. `LeastWork`: the smallest `work`. Ties go to the transaction with the larger `id`."],
  ["The victim is a member of the cycle.","The choice depends only on the compared attribute and the ids."],
  ["Permuting the cycle does not change which transaction is chosen.","Adding a transaction with a strictly worse attribute (older, more locks, more work) never changes the victim.","A one-element cycle's victim is that element."],
  ["cycle [(id 1, start 10), (id 2, start 30), (id 3, start 20)] Youngest -> id 2"],
  ["Each policy.","Tie-breaks.","A property: permutation invariance."],
  src=("src/concurrency/victim.rs", '''
//! Which transaction of a deadlock cycle is aborted.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TxnInfo {
    pub id: u32,
    pub start_ts: u64,
    pub locks: usize,
    pub work: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VictimPolicy {
    Youngest,
    FewestLocks,
    LeastWork,
}

pub fn choose_victim(policy: VictimPolicy, cycle: &[TxnInfo]) -> Option<usize> {
    // @begin 4d-c3
    let key = |t: &TxnInfo| -> (i128, u32) {
        match policy {
            VictimPolicy::Youngest => (-(t.start_ts as i128), u32::MAX - t.id),
            VictimPolicy::FewestLocks => (t.locks as i128, u32::MAX - t.id),
            VictimPolicy::LeastWork => (t.work as i128, u32::MAX - t.id),
        }
    };
    (0..cycle.len()).min_by_key(|&i| key(&cycle[i]))
    //~ todo!("4d-c3: the best candidate by the policy's attribute; the larger id on ties")
    // @end
}
'''),
  test=("tests/stages_4d.rs", '''
use bustub::concurrency::victim::{choose_victim, TxnInfo, VictimPolicy::*};

fn t(id: u32, start_ts: u64, locks: usize, work: u64) -> TxnInfo {
    TxnInfo { id, start_ts, locks, work }
}

fn cycle() -> Vec<TxnInfo> {
    vec![t(1, 10, 5, 100), t(2, 30, 9, 50), t(3, 20, 2, 70)]
}

#[test]
fn s4d_c3_each_policy_picks_by_its_attribute() {
    assert_eq!(choose_victim(Youngest, &cycle()), Some(1));
    assert_eq!(choose_victim(FewestLocks, &cycle()), Some(2));
    assert_eq!(choose_victim(LeastWork, &cycle()), Some(1));
}

#[test]
fn s4d_c3_ties_go_to_the_larger_id() {
    let c = vec![t(4, 10, 3, 5), t(9, 10, 3, 5), t(7, 10, 3, 5)];
    for p in [Youngest, FewestLocks, LeastWork] {
        assert_eq!(choose_victim(p, &c), Some(1), "{p:?}");
    }
}

#[test]
fn s4d_c3_empty_and_single_cycles() {
    assert_eq!(choose_victim(Youngest, &[]), None);
    assert_eq!(choose_victim(LeastWork, &[t(1, 1, 1, 1)]), Some(0));
}

#[test]
fn s4d_c3_the_order_of_the_cycle_does_not_change_who_is_chosen() {
    let c = cycle();
    let r = vec![t(3, 20, 2, 70), t(2, 30, 9, 50), t(1, 10, 5, 100)];
    for p in [Youngest, FewestLocks, LeastWork] {
        let (a, b) = (choose_victim(p, &c).unwrap(), choose_victim(p, &r).unwrap());
        assert_eq!(c[a].id, r[b].id, "{p:?}");
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the same transaction is chosen whatever the order of the cycle.
    #[test]
    fn s4d_c3_property_the_choice_does_not_depend_on_the_order(raw in proptest::collection::vec((0u64..5, 0usize..4, 0u64..5), 1..6), policy in prop::sample::select(vec![Youngest, FewestLocks, LeastWork])) {
        let c: Vec<TxnInfo> = raw.iter().enumerate().map(|(i, &(s, l, w))| t(i as u32 + 1, s, l, w)).collect();
        let chosen = c[choose_victim(policy, &c).unwrap()].id;
        let mut rev = c.clone();
        rev.reverse();
        prop_assert_eq!(rev[choose_victim(policy, &rev).unwrap()].id, chosen);
        let attr = |x: &TxnInfo| match policy { Youngest => -(x.start_ts as i128), FewestLocks => x.locks as i128, LeastWork => x.work as i128 };
        let best = c.iter().map(attr).min().unwrap();
        let v = c.iter().find(|x| x.id == chosen).unwrap();
        prop_assert_eq!(attr(v), best);
        prop_assert!(c.iter().filter(|x| attr(x) == best).all(|x| x.id <= chosen));
    }
}
''')))

CH.append(C("4d-c4", M4D, "93-challenge-barging", "debug", "Challenge: barging", "easy", "stages_4d::s4d_c4",
  ["finding the grant rule that lets a reader overtake a blocked writer"],
  ["lock-modes-and-two-phase-locking","condvars-and-blocking-queues","property-testing-and-fuzzing"],
  "`grantable` in `src/concurrency/grant.rs` decides which waiting requests of one lock may be granted **now**, given the modes of the current holders and the waiting queue in arrival order. The rule is fair: requests are considered in order and the scan **stops** at the first one that cannot be granted. It looks right, and a reader gets in past a waiting writer. Find the bug and fix it.",
  "Without the stop, readers keep arriving, each compatible with the current readers, and the writer at the head of the queue never runs: starvation. Fairness is one control-flow keyword, and this is the version of it that is easy to get wrong because the loop still produces plausible answers.",
  ["`grantable(holders, waiting)` returns the indexes (into `waiting`) of the requests to grant now, in order.","A request is granted if it is compatible with every holder **and** with every request granted before it in this call; the scan stops at the first request that is not granted."],
  ["The granted set is always a prefix of the waiting queue.","Granted requests are pairwise compatible and compatible with all holders."],
  ["If the first waiter is incompatible with a holder, nothing is granted.","Adding a waiter at the end never changes which earlier waiters are granted.","With no holders, the first waiter is always granted."],
  ["holders [S]; waiting [X, S] -> none (the reader may not pass the writer)","holders []; waiting [S, S, X, S] -> [0, 1]"],
  ["Prefix property and the stop.","Compatible runs.","A property: the granted set is a compatible prefix."],
  src=("src/concurrency/grant.rs", '''
//! Which waiting lock requests may be granted now.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    S,
    X,
}

fn compatible(a: Mode, b: Mode) -> bool {
    a == Mode::S && b == Mode::S
}

pub fn grantable(holders: &[Mode], waiting: &[Mode]) -> Vec<usize> {
    let mut granted: Vec<usize> = Vec::new();
    for (i, &m) in waiting.iter().enumerate() {
        let ok = holders.iter().all(|&h| compatible(h, m)) && granted.iter().all(|&g| compatible(waiting[g], m));
        if ok {
            granted.push(i);
        } else {
            // @begin 4d-c4
            break;
            //~ continue;
            // @end
        }
    }
    granted
}
'''),
  test=("tests/stages_4d.rs", '''
use bustub::concurrency::grant::{grantable, Mode::*};

#[test]
fn s4d_c4_a_reader_may_not_pass_a_waiting_writer() {
    assert_eq!(grantable(&[S], &[X, S]), Vec::<usize>::new());
    assert_eq!(grantable(&[S, S], &[X, S, S]), Vec::<usize>::new());
}

#[test]
fn s4d_c4_readers_at_the_front_are_granted_together_up_to_the_first_writer() {
    assert_eq!(grantable(&[], &[S, S, X, S]), vec![0, 1]);
    assert_eq!(grantable(&[S], &[S, S, X]), vec![0, 1]);
}

#[test]
fn s4d_c4_a_writer_at_the_front_goes_alone_when_free() {
    assert_eq!(grantable(&[], &[X, S, S]), vec![0]);
    assert_eq!(grantable(&[X], &[S]), Vec::<usize>::new());
}

#[test]
fn s4d_c4_nothing_waiting_nothing_granted() {
    assert_eq!(grantable(&[S], &[]), Vec::<usize>::new());
    assert_eq!(grantable(&[], &[]), Vec::<usize>::new());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the granted requests are a prefix of the queue, compatible with the holders and with each other; and the first refused one is
    /// really incompatible with a holder or an earlier grant.
    #[test]
    fn s4d_c4_property_the_grant_is_a_compatible_prefix(holders in proptest::collection::vec(prop_oneof![Just(S), Just(X)], 0..3), waiting in proptest::collection::vec(prop_oneof![Just(S), Just(X)], 0..6)) {
        // holders are mutually compatible in a real system: keep only legal sets
        prop_assume!(holders.iter().all(|&h| h == S) || holders.len() <= 1);
        let g = grantable(&holders, &waiting);
        prop_assert_eq!(g.clone(), (0..g.len()).collect::<Vec<_>>());
        let all_ok = |upto: usize| waiting[..upto].iter().all(|&a| holders.iter().all(|&h| h == S && a == S)) && (upto <= 1 || waiting[..upto].iter().all(|&a| a == S));
        let _ = all_ok;
        let mut modes: Vec<_> = holders.clone();
        modes.extend(g.iter().map(|&i| waiting[i]));
        prop_assert!(modes.len() <= 1 || modes.iter().all(|&m| m == S));
        if g.len() < waiting.len() {
            let next = waiting[g.len()];
            prop_assert!(!(modes.iter().all(|&m| m == S && next == S)), "the first refused request was grantable");
        }
    }
}
''')))

CH.append(C("4d-c5", M4D, "94-challenge-lock-escalation", "build", "Challenge: lock escalation", "easy", "stages_4d::s4d_c5",
  ["trading many fine locks for one coarse one","what a row lock request means once the table is locked"],
  ["lock-modes-and-two-phase-locking","coarse-and-fine-grained-locking"],
  "`Escalator` in `src/concurrency/escalation.rs`: bookkeeping for **lock escalation**. `row_lock(txn, table, row)` records a row lock; when a transaction holds **more than `threshold`** row locks on one table, they are replaced by a single table lock: the call returns `Escalate { table, released }` listing the row locks given up. Once a transaction holds the table lock, further row requests on that table are `Covered`.",
  "Every lock costs memory and bookkeeping; a transaction that updates a million rows should not keep a million lock entries. Escalation is the standard answer (SQL Server, DB2, Oracle's alternatives), and the cost is concurrency: other transactions can no longer touch the table's other rows. The mechanism is a counter and a rule about what is subsumed.",
  ["`row_lock(txn, table, row)` returns `Granted` (recorded; count at most `threshold` after it), `Covered` (the transaction already holds the table lock), or `Escalate { table, released }` when the count would exceed `threshold`: the rows are released, the table lock is now held and the new row is covered too.","`holds_table(txn, table)`, `row_count(txn, table)`; `release_all(txn)` forgets everything.","Duplicate row locks are not counted twice."],
  ["After any call, `row_count(txn, table) <= threshold`.","A transaction that holds the table lock holds no row locks on that table.","`released` contains exactly the rows that were held before the escalation."],
  ["Escalation happens exactly when the `threshold + 1`-th distinct row is requested.","Escalating one table never affects the same transaction's rows on another table, or another transaction.","After escalation every further request on the table is `Covered`."],
  ["threshold 2: rows 1, 2 granted; row 3 -> Escalate { released [1, 2] }; row 4 -> Covered"],
  ["Counting, escalating, covering.","Independent tables and transactions.","A property against a model."],
  src=("src/concurrency/escalation.rs", '''
//! Lock escalation: many row locks become one table lock.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, PartialEq, Eq)]
pub enum RowLockResult {
    Granted,
    Covered,
    Escalate { table: u32, released: Vec<u64> },
}

pub struct Escalator {
    // @begin 4d-c5
    threshold: usize,
    rows: BTreeMap<(u32, u32), BTreeSet<u64>>,
    tables: BTreeSet<(u32, u32)>,
    //~ _esc: (),
    // @end
}

impl Escalator {
    pub fn new(threshold: usize) -> Escalator {
        // @begin 4d-c5
        Escalator { threshold, rows: BTreeMap::new(), tables: BTreeSet::new() }
        //~ todo!("4d-c5: nothing locked")
        // @end
    }

    pub fn row_lock(&mut self, txn: u32, table: u32, row: u64) -> RowLockResult {
        // @begin 4d-c5
        if self.tables.contains(&(txn, table)) {
            return RowLockResult::Covered;
        }
        let set = self.rows.entry((txn, table)).or_default();
        if set.contains(&row) {
            return RowLockResult::Granted;
        }
        if set.len() + 1 > self.threshold {
            let released: Vec<u64> = std::mem::take(set).into_iter().collect();
            self.rows.remove(&(txn, table));
            self.tables.insert((txn, table));
            return RowLockResult::Escalate { table, released };
        }
        set.insert(row);
        RowLockResult::Granted
        //~ todo!("4d-c5: count the transaction's row locks on the table; past the threshold replace them by a table lock")
        // @end
    }

    pub fn holds_table(&self, txn: u32, table: u32) -> bool {
        // @begin 4d-c5
        self.tables.contains(&(txn, table))
        //~ todo!("4d-c5: does the transaction hold the table lock")
        // @end
    }

    pub fn row_count(&self, txn: u32, table: u32) -> usize {
        // @begin 4d-c5
        self.rows.get(&(txn, table)).map_or(0, BTreeSet::len)
        //~ todo!("4d-c5: how many row locks")
        // @end
    }

    pub fn release_all(&mut self, txn: u32) {
        // @begin 4d-c5
        self.rows.retain(|&(t, _), _| t != txn);
        self.tables.retain(|&(t, _)| t != txn);
        //~ todo!("4d-c5: forget every lock of the transaction")
        // @end
    }
}
'''),
  test=("tests/stages_4d.rs", '''
use bustub::concurrency::escalation::{Escalator, RowLockResult::*};

#[test]
fn s4d_c5_the_row_after_the_threshold_escalates_and_then_everything_is_covered() {
    let mut e = Escalator::new(2);
    assert_eq!(e.row_lock(1, 7, 10), Granted);
    assert_eq!(e.row_lock(1, 7, 11), Granted);
    assert_eq!(e.row_lock(1, 7, 12), Escalate { table: 7, released: vec![10, 11] });
    assert!(e.holds_table(1, 7));
    assert_eq!(e.row_count(1, 7), 0);
    assert_eq!(e.row_lock(1, 7, 13), Covered);
}

#[test]
fn s4d_c5_the_same_row_twice_is_not_counted_twice() {
    let mut e = Escalator::new(2);
    for _ in 0..5 {
        assert_eq!(e.row_lock(1, 7, 10), Granted);
    }
    assert_eq!(e.row_count(1, 7), 1);
}

#[test]
fn s4d_c5_tables_and_transactions_are_counted_separately() {
    let mut e = Escalator::new(1);
    assert_eq!(e.row_lock(1, 7, 1), Granted);
    assert_eq!(e.row_lock(1, 8, 1), Granted);
    assert_eq!(e.row_lock(2, 7, 1), Granted);
    assert!(matches!(e.row_lock(1, 7, 2), Escalate { .. }));
    assert!(!e.holds_table(1, 8));
    assert!(!e.holds_table(2, 7));
    assert_eq!(e.row_lock(1, 8, 2), Escalate { table: 8, released: vec![1] });
}

#[test]
fn s4d_c5_release_all_forgets_the_transaction() {
    let mut e = Escalator::new(1);
    e.row_lock(1, 7, 1);
    e.row_lock(1, 7, 2);
    assert!(e.holds_table(1, 7));
    e.release_all(1);
    assert!(!e.holds_table(1, 7));
    assert_eq!(e.row_lock(1, 7, 3), Granted);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: row counts never exceed the threshold; escalation happens exactly at the threshold + 1-th distinct row; released rows are the held ones.
    #[test]
    fn s4d_c5_property_escalation_follows_the_count(threshold in 1usize..4, reqs in proptest::collection::vec((1u32..3, 1u32..3, 0u64..6), 0..30)) {
        let mut e = Escalator::new(threshold);
        let mut rows: std::collections::BTreeMap<(u32, u32), std::collections::BTreeSet<u64>> = Default::default();
        let mut tables: std::collections::BTreeSet<(u32, u32)> = Default::default();
        for (txn, table, row) in reqs {
            let key = (txn, table);
            let got = e.row_lock(txn, table, row);
            if tables.contains(&key) {
                prop_assert_eq!(got, Covered);
            } else {
                let set = rows.entry(key).or_default();
                if set.contains(&row) {
                    prop_assert_eq!(got, Granted);
                } else if set.len() + 1 > threshold {
                    prop_assert_eq!(got, Escalate { table, released: set.iter().copied().collect() });
                    rows.remove(&key);
                    tables.insert(key);
                } else {
                    prop_assert_eq!(got, Granted);
                    set.insert(row);
                }
            }
            prop_assert!(e.row_count(txn, table) <= threshold);
            prop_assert_eq!(e.holds_table(txn, table), tables.contains(&key));
        }
    }
}
''')))
