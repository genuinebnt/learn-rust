from _c import C
M4A, M4B, M4C, M4D = "20-timestamps-and-version-chains", "21-mvcc-writes-abort-and-gc", "22-acid-logging-and-recovery", "23-the-lock-manager"
CH = []

CH.append(C("4a-c1", M4A, "90-challenge-a-read-view", "build", "Challenge: a read view", "easy", "stages_4a::s4a_c1",
  ["deciding which transactions' writes a snapshot may see from the set that was active when it began","the id-based alternative to commit timestamps"],
  ["multi-version-concurrency-control","snapshot-isolation","logical-clocks-and-timestamps"],
  "`ReadView` in `src/concurrency/read_view.rs`: the snapshot rule used by InnoDB and others, based on **transaction ids** rather than commit timestamps. When a transaction begins it records the set of transactions that are active and the id the next transaction will get. `visible(writer)` says whether a version written by transaction `writer` is visible to it.",
  "Commit timestamps need a number assigned at commit; ids are assigned at begin, so a snapshot must remember who had not finished. The rule is three lines, but each line is an easy one to get backwards: a version is visible if its writer committed before the snapshot began. In id terms, that is \"older than the snapshot, and not in the active set\", plus your own writes.",
  ["`ReadView::new(own_id, active_ids, next_id)`: `active_ids` are the ids of transactions that had begun and not finished (they may include `own_id`); `next_id` is the id that will be given to the next transaction.","`visible(writer)` is true for `writer == own_id`; false for `writer >= next_id` (began after the snapshot) and for any writer in `active_ids`; true otherwise."],
  ["A writer is visible exactly when it is `own_id`, or it began before the snapshot and was not active.","The answer for a given writer never changes during the life of the view."],
  ["Adding an id to the active set can only turn a visible writer invisible.","Raising `next_id` can only turn invisible writers (those that began after) visible, never an active one.","`own_id` is always visible to itself."],
  ["own 5, active [3, 5, 7], next 9: visible(2) yes, visible(3) no, visible(4) yes, visible(5) yes, visible(7) no, visible(9) no"],
  ["Each rule on a small view.","Edge ids: 0, own id, the next id.","A property against a set model."],
  src=("src/concurrency/read_view.rs", '''
//! A snapshot defined by transaction ids.

use std::collections::BTreeSet;

pub struct ReadView {
    // @begin 4a-c1
    own: u64,
    active: BTreeSet<u64>,
    next_id: u64,
    //~ _view: (),
    // @end
}

impl ReadView {
    pub fn new(own_id: u64, active_ids: &[u64], next_id: u64) -> ReadView {
        // @begin 4a-c1
        ReadView { own: own_id, active: active_ids.iter().copied().collect(), next_id }
        //~ todo!("4a-c1: remember who was active and where ids stood")
        // @end
    }

    /// Is a version written by transaction `writer` visible to this snapshot?
    pub fn visible(&self, writer: u64) -> bool {
        // @begin 4a-c1
        if writer == self.own {
            return true;
        }
        writer < self.next_id && !self.active.contains(&writer)
        //~ todo!("4a-c1: your own writes; older and not active")
        // @end
    }
}
'''),
  test=("tests/stages_4a.rs", '''
use bustub::concurrency::read_view::ReadView;
use std::collections::BTreeSet;

#[test]
fn s4a_c1_the_three_rules_on_a_small_view() {
    let v = ReadView::new(5, &[3, 5, 7], 9);
    assert!(v.visible(2), "committed before the snapshot");
    assert!(!v.visible(3), "was active");
    assert!(v.visible(4));
    assert!(v.visible(5), "my own writes");
    assert!(!v.visible(7));
    assert!(!v.visible(9), "began after the snapshot");
    assert!(!v.visible(100));
}

#[test]
fn s4a_c1_an_empty_active_set_sees_every_older_transaction() {
    let v = ReadView::new(10, &[], 10);
    assert!((0..10).all(|w| v.visible(w)));
    assert!(v.visible(10));
    assert!(!v.visible(11));
}

#[test]
fn s4a_c1_own_writes_are_visible_even_when_listed_active() {
    let v = ReadView::new(3, &[3], 4);
    assert!(v.visible(3));
}

#[test]
fn s4a_c1_the_boundary_id_is_exclusive() {
    let v = ReadView::new(1, &[], 6);
    assert!(v.visible(5));
    assert!(!v.visible(6));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against the definition with sets, and adding an active id only removes visibility.
    #[test]
    fn s4a_c1_property_visibility_follows_the_definition(own in 0u64..12, active in proptest::collection::btree_set(0u64..12, 0..6), next in 0u64..14, extra in 0u64..12, w in 0u64..16) {
        let act: Vec<u64> = active.iter().copied().collect();
        let v = ReadView::new(own, &act, next);
        let want = w == own || (w < next && !active.contains(&w));
        prop_assert_eq!(v.visible(w), want);
        let mut more: BTreeSet<u64> = active.clone();
        more.insert(extra);
        let v2 = ReadView::new(own, &more.iter().copied().collect::<Vec<_>>(), next);
        if v2.visible(w) { prop_assert!(v.visible(w)); }
    }
}
''')))

CH.append(C("4a-c2", M4A, "91-challenge-reading-a-version-chain", "build", "Challenge: reading a version chain", "medium", "stages_4a::s4a_c2",
  ["picking the version a reader at a timestamp may see","your own uncommitted version, and a delete marker"],
  ["multi-version-concurrency-control","snapshot-isolation"],
  "`read_version` in `src/concurrency/version_read.rs`: a row's versions are kept **newest first** as `Version { writer, stamp, value }` where `stamp` is `Commit(ts)` for a committed version or `Pending` for one its writer has not committed; `value` is `Some(v)` or `None` (a delete). Return what a reader with a **read timestamp** and its own transaction id sees: the newest version that is committed with `ts <= read_ts`, or is its own pending one.",
  "This is the core of snapshot isolation in twenty lines. A reader never blocks and never sees a half-finished write; it sees the newest committed state as of its timestamp, plus whatever it wrote itself. Everything else in MVCC (garbage collection, conflicts, validation) is built on knowing exactly which version this function picks.",
  ["Walk the chain from the newest version. A `Pending` version of another writer is skipped. A `Pending` version of the reader itself is visible. A `Commit(ts)` is visible iff `ts <= read_ts`.","The first visible version decides: its `value` is the answer (`None` for a delete: the row does not exist for this reader).","If no version is visible, the row does not exist for this reader."],
  ["The answer is the value of at most one version of the chain.","A reader's own pending write always wins over committed versions."],
  ["Raising `read_ts` never shows an older version than before.","Another transaction's pending versions never change a reader's answer.","Committing a reader's own pending version at `ts <= read_ts` does not change its answer."],
  ["chain [P(txn 7, 'c'), C(ts 5, 'b'), C(ts 2, 'a')]: reader ts 4 -> 'a'; ts 5 -> 'b'; txn 7 at ts 5 -> 'c'","chain [C(ts 5, delete), C(ts 2, 'a')]: ts 3 -> 'a'; ts 6 -> none"],
  ["Committed, pending, own and deleted versions.","Boundaries of the timestamp.","A property against a scan."],
  src=("src/concurrency/version_read.rs", '''
//! Which version of a row does a reader see?

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Stamp {
    Commit(u64),
    Pending,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Version {
    pub writer: u64,
    pub stamp: Stamp,
    /// `None` is a delete.
    pub value: Option<i64>,
}

/// `chain` is newest first. Returns the value the reader sees (`None`: the row does not exist for it).
pub fn read_version(chain: &[Version], read_ts: u64, reader: u64) -> Option<i64> {
    // @begin 4a-c2
    for v in chain {
        let visible = match v.stamp {
            Stamp::Commit(ts) => ts <= read_ts,
            Stamp::Pending => v.writer == reader,
        };
        if visible {
            return v.value;
        }
    }
    None
    //~ todo!("4a-c2: the first version in the chain that this reader may see decides")
    // @end
}
'''),
  test=("tests/stages_4a.rs", '''
use bustub::concurrency::version_read::{read_version, Stamp::*, Version};

fn v(writer: u64, stamp: bustub::concurrency::version_read::Stamp, value: Option<i64>) -> Version {
    Version { writer, stamp, value }
}

fn chain() -> Vec<Version> {
    vec![v(7, Pending, Some(30)), v(2, Commit(5), Some(20)), v(1, Commit(2), Some(10))]
}

#[test]
fn s4a_c2_a_reader_sees_the_newest_committed_version_at_its_timestamp() {
    assert_eq!(read_version(&chain(), 1, 9), None, "nothing was committed yet at ts 1");
    assert_eq!(read_version(&chain(), 4, 9), Some(10));
    assert_eq!(read_version(&chain(), 5, 9), Some(20));
    assert_eq!(read_version(&chain(), 100, 9), Some(20));
}

#[test]
fn s4a_c2_the_writer_sees_its_own_pending_version() {
    assert_eq!(read_version(&chain(), 5, 7), Some(30));
    assert_eq!(read_version(&chain(), 0, 7), Some(30), "its own write is visible whatever the timestamp");
}

#[test]
fn s4a_c2_a_committed_delete_hides_the_row_after_its_timestamp() {
    let c = vec![v(3, Commit(5), None), v(1, Commit(2), Some(10))];
    assert_eq!(read_version(&c, 3, 9), Some(10));
    assert_eq!(read_version(&c, 6, 9), None);
}

#[test]
fn s4a_c2_a_pending_delete_by_someone_else_is_invisible() {
    let c = vec![v(7, Pending, None), v(1, Commit(2), Some(10))];
    assert_eq!(read_version(&c, 5, 9), Some(10));
    assert_eq!(read_version(&c, 5, 7), None, "but the deleter sees its own delete");
}

#[test]
fn s4a_c2_an_empty_chain_is_no_row() {
    assert_eq!(read_version(&[], 10, 1), None);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: equals a scan for the newest visible version; raising the timestamp never reads an older version.
    #[test]
    fn s4a_c2_property_reading_equals_a_scan(ts_list in proptest::collection::btree_set(1u64..20, 0..6), pending in proptest::option::of((0u64..4, proptest::option::of(0i64..50))), read_ts in 0u64..22, reader in 0u64..4) {
        let mut stamps: Vec<u64> = ts_list.into_iter().collect();
        stamps.reverse(); // newest first
        let mut chain: Vec<Version> = Vec::new();
        if let Some((w, val)) = pending { chain.push(v(w, Pending, val)); }
        for (i, ts) in stamps.iter().enumerate() { chain.push(v(9, Commit(*ts), if i % 3 == 2 { None } else { Some(*ts as i64) })); }
        let want = chain.iter().find(|x| match x.stamp { Commit(t) => t <= read_ts, Pending => x.writer == reader }).and_then(|x| x.value);
        prop_assert_eq!(read_version(&chain, read_ts, reader), want);
        // a later reader never sees an older committed version: compare the committed-only chains
        let committed: Vec<Version> = chain.iter().filter(|x| x.stamp != Pending).cloned().collect();
        let early = committed.iter().position(|x| matches!(x.stamp, Commit(t) if t <= read_ts));
        let late = committed.iter().position(|x| matches!(x.stamp, Commit(t) if t <= read_ts + 5));
        if let (Some(e), Some(l)) = (early, late) { prop_assert!(l <= e, "a later timestamp must not pick an older version"); }
    }
}
''')))

CH.append(C("4a-c3", M4A, "92-challenge-the-snapshot-with-a-hole", "debug", "Challenge: the snapshot with a hole", "medium", "stages_4a::s4a_c3",
  ["finding a timestamp-assignment bug that gives a snapshot a gap","why a read timestamp must not pass an unfinished commit"],
  ["logical-clocks-and-timestamps","snapshot-isolation","property-testing-and-fuzzing"],
  "`src/concurrency/ts_oracle.rs` hands out timestamps: `reserve()` gives the next commit timestamp to a transaction that is about to commit, `finish(ts)` says that commit's writes are all in place, and `begin()` gives a new reader its read timestamp. It looks right, and a reader can be given a timestamp that sees commit 6 but not commit 5. Find the bug and fix it.",
  "A snapshot must be a **prefix** of the commit order: everything up to the read timestamp, nothing after. Commits can finish out of order (5 reserved first, 6 finishes first), and a read timestamp that jumps over an unfinished commit shows a state that never existed, with the effects of 6 and without the effects of 5 that 6 may depend on.",
  ["`reserve()` returns 1, 2, 3, ... in order; `finish(ts)` marks that commit as complete (finishing twice or an unknown ts is ignored).","`begin()` returns the largest `t` such that **every** reserved timestamp `<= t` has finished (0 if none have, and `reserved` if all have)."],
  ["For the read timestamp `t` returned by `begin`, every reserved `ts <= t` is finished.","No finished commit `<= t` is missing from the snapshot: `t` is the largest such value."],
  ["`begin()` never decreases as commits finish.","`begin()` is at most the smallest unfinished reserved timestamp minus one.","Finishing in any order ends with `begin() == reserved`."],
  ["reserve 1, 2, 3; finish 2 -> begin 0; finish 1 -> begin 2; finish 3 -> begin 3"],
  ["Out-of-order finishes.","Nothing reserved yet.","A property against the definition."],
  src=("src/concurrency/ts_oracle.rs", '''
//! A timestamp oracle: commit timestamps and read timestamps.

use std::collections::BTreeSet;

#[derive(Default)]
pub struct TsOracle {
    reserved: u64,
    finished: BTreeSet<u64>,
}

impl TsOracle {
    pub fn new() -> TsOracle {
        TsOracle::default()
    }

    /// The next commit timestamp.
    pub fn reserve(&mut self) -> u64 {
        self.reserved += 1;
        self.reserved
    }

    /// The commit with timestamp `ts` has put all its writes in place.
    pub fn finish(&mut self, ts: u64) {
        if ts >= 1 && ts <= self.reserved {
            self.finished.insert(ts);
        }
    }

    /// The read timestamp for a new transaction.
    pub fn begin(&self) -> u64 {
        // @begin 4a-c3
        let mut t = 0;
        while t < self.reserved && self.finished.contains(&(t + 1)) {
            t += 1;
        }
        t
        //~ self.finished.iter().next_back().copied().unwrap_or(0)
        // @end
    }
}
'''),
  test=("tests/stages_4a.rs", '''
use bustub::concurrency::ts_oracle::TsOracle;

#[test]
fn s4a_c3_a_commit_that_finished_early_does_not_pull_the_snapshot_over_a_gap() {
    let mut o = TsOracle::new();
    assert_eq!((o.reserve(), o.reserve(), o.reserve()), (1, 2, 3));
    assert_eq!(o.begin(), 0);
    o.finish(2);
    assert_eq!(o.begin(), 0, "commit 1 is not finished: a snapshot at 2 would show commit 2 without commit 1");
    o.finish(1);
    assert_eq!(o.begin(), 2);
    o.finish(3);
    assert_eq!(o.begin(), 3);
}

#[test]
fn s4a_c3_nothing_reserved_means_timestamp_zero() {
    assert_eq!(TsOracle::new().begin(), 0);
}

#[test]
fn s4a_c3_finishing_in_order_advances_one_at_a_time() {
    let mut o = TsOracle::new();
    for i in 1..=5 {
        o.reserve();
        o.finish(i);
        assert_eq!(o.begin(), i);
    }
}

#[test]
fn s4a_c3_odd_calls_are_ignored() {
    let mut o = TsOracle::new();
    o.reserve();
    o.finish(5);
    o.finish(0);
    assert_eq!(o.begin(), 0);
    o.finish(1);
    o.finish(1);
    assert_eq!(o.begin(), 1);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: `begin` is the largest t with every reserved ts <= t finished, and never decreases.
    #[test]
    fn s4a_c3_property_the_read_timestamp_is_a_finished_prefix(n in 1u64..8, order in proptest::collection::vec(0usize..8, 0..16)) {
        let mut o = TsOracle::new();
        for _ in 0..n { o.reserve(); }
        let mut done = std::collections::BTreeSet::new();
        let mut last = 0;
        for k in order {
            let ts = (k as u64 % n) + 1;
            o.finish(ts);
            done.insert(ts);
            let want = (0..n).take_while(|i| done.contains(&(i + 1))).count() as u64;
            let got = o.begin();
            prop_assert_eq!(got, want);
            prop_assert!(got >= last);
            last = got;
        }
    }
}
''')))

CH.append(C("4a-c4", M4A, "93-challenge-undoing-a-partial-update", "build", "Challenge: undoing a partial update", "medium", "stages_4a::s4a_c4",
  ["storing only the columns that changed as an undo record","reconstructing older versions by applying undo records newest first"],
  ["rolling-back-with-undo-logs","multi-version-concurrency-control"],
  "`make_undo` and `apply_undo` in `src/concurrency/undo.rs`: a tuple is `Vec<i64>` or absent (`None`). `make_undo(old, new)` records how to get back from `new` to `old`: for an update, only the columns that **differ** (a mask and their old values); for a delete or an insert, a flag. `apply_undo(tuple, log)` applies one log to the newer version and returns the older one.",
  "Storing the whole old row for every update wastes space when one column of fifty changed, which is why systems store *deltas*. Reading an old version then means walking back from the newest, applying each delta. Getting the three cases (insert, update, delete) and the absent tuple right is the whole exercise, and the property that ties them together is simple: undoing the change gives back the old version.",
  ["`make_undo(old: Option<&[i64]>, new: Option<&[i64]>) -> UndoLog`: `old == None` (the change was an insert) records `Remove`; `new == None` (a delete) records `Restore(whole old row)`; both present records `Columns { mask, values }` with exactly the differing columns, in column order.","`apply_undo(tuple: Option<&[i64]>, log) -> Option<Vec<i64>>`: `Remove` gives `None`; `Restore(row)` gives that row; `Columns` overwrites the masked columns of the tuple (which must exist).","Tuples have a fixed number of columns."],
  ["`apply_undo(new, make_undo(old, new)) == old` for every pair.","A `Columns` log's mask has no bit set for an equal column, and a log is empty (no bits) only for an unchanged row."],
  ["Undo logs of a chain of updates, applied newest first, reproduce every older version.","The size of an update log is proportional to the number of changed columns.","Making a log from equal rows and applying it changes nothing."],
  ["old [1,2,3], new [1,9,3] -> columns {1: 2}; apply to [1,9,3] -> [1,2,3]","old None, new [4] -> Remove; old [4], new None -> Restore([4])"],
  ["The three kinds of change.","A chain of updates undone one by one.","A property for any pair and any chain."],
  src=("src/concurrency/undo.rs", '''
//! Delta undo records for MVCC.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum UndoLog {
    /// The change created the tuple: undoing it removes it.
    Remove,
    /// The change deleted the tuple: undoing it restores the whole row.
    Restore(Vec<i64>),
    /// The change updated some columns: `mask[i]` says column `i` differs; `values` holds the old values of exactly those columns, in order.
    Columns { mask: Vec<bool>, values: Vec<i64> },
}

pub fn make_undo(old: Option<&[i64]>, new: Option<&[i64]>) -> UndoLog {
    // @begin 4a-c4
    match (old, new) {
        (None, _) => UndoLog::Remove,
        (Some(o), None) => UndoLog::Restore(o.to_vec()),
        (Some(o), Some(n)) => {
            let mask: Vec<bool> = o.iter().zip(n).map(|(a, b)| a != b).collect();
            let values = o.iter().zip(&mask).filter(|(_, &m)| m).map(|(&v, _)| v).collect();
            UndoLog::Columns { mask, values }
        }
    }
    //~ todo!("4a-c4: an insert is undone by removing, a delete by restoring, an update by the changed columns only")
    // @end
}

pub fn apply_undo(tuple: Option<&[i64]>, log: &UndoLog) -> Option<Vec<i64>> {
    // @begin 4a-c4
    match log {
        UndoLog::Remove => None,
        UndoLog::Restore(row) => Some(row.clone()),
        UndoLog::Columns { mask, values } => {
            let mut row = tuple?.to_vec();
            let mut vals = values.iter();
            for (c, &m) in row.iter_mut().zip(mask) {
                if m {
                    *c = *vals.next()?;
                }
            }
            Some(row)
        }
    }
    //~ todo!("4a-c4: remove, restore, or write the masked columns back")
    // @end
}
'''),
  test=("tests/stages_4a.rs", '''
use bustub::concurrency::undo::{apply_undo, make_undo, UndoLog};

#[test]
fn s4a_c4_an_update_records_only_the_changed_columns() {
    let log = make_undo(Some(&[1, 2, 3]), Some(&[1, 9, 3]));
    assert_eq!(log, UndoLog::Columns { mask: vec![false, true, false], values: vec![2] });
    assert_eq!(apply_undo(Some(&[1, 9, 3]), &log), Some(vec![1, 2, 3]));
}

#[test]
fn s4a_c4_an_insert_is_undone_by_removing_and_a_delete_by_restoring() {
    assert_eq!(make_undo(None, Some(&[4])), UndoLog::Remove);
    assert_eq!(apply_undo(Some(&[4]), &UndoLog::Remove), None);
    let del = make_undo(Some(&[4, 5]), None);
    assert_eq!(del, UndoLog::Restore(vec![4, 5]));
    assert_eq!(apply_undo(None, &del), Some(vec![4, 5]));
}

#[test]
fn s4a_c4_an_unchanged_row_has_an_empty_mask_and_changes_nothing() {
    let log = make_undo(Some(&[7, 8]), Some(&[7, 8]));
    assert_eq!(log, UndoLog::Columns { mask: vec![false, false], values: vec![] });
    assert_eq!(apply_undo(Some(&[7, 8]), &log), Some(vec![7, 8]));
}

#[test]
fn s4a_c4_a_chain_of_updates_is_walked_back_newest_first() {
    let versions = [vec![1, 1, 1], vec![1, 2, 1], vec![3, 2, 1], vec![3, 2, 9]];
    let logs: Vec<UndoLog> = (1..versions.len()).map(|i| make_undo(Some(&versions[i - 1]), Some(&versions[i]))).collect();
    let mut cur = Some(versions[3].clone());
    for i in (0..3).rev() {
        cur = apply_undo(cur.as_deref(), &logs[i]);
        assert_eq!(cur.as_ref(), Some(&versions[i]), "undoing back to version {i}");
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: undoing a change gives back the old version, for any pair of versions and any chain.
    #[test]
    fn s4a_c4_property_undo_restores_the_old_version(cols in 1usize..5, a in proptest::collection::vec(-3i64..3, 5), b in proptest::collection::vec(-3i64..3, 5), c in proptest::collection::vec(-3i64..3, 5), kinds in (any::<bool>(), any::<bool>())) {
        let (a, b, c) = (a[..cols].to_vec(), b[..cols].to_vec(), c[..cols].to_vec());
        let old = if kinds.0 { Some(a.as_slice()) } else { None };
        let new = if kinds.1 { Some(b.as_slice()) } else { None };
        let log = make_undo(old, new);
        prop_assert_eq!(apply_undo(new, &log), old.map(|r| r.to_vec()));
        if let UndoLog::Columns { mask, values } = &log {
            prop_assert_eq!(values.len(), mask.iter().filter(|m| **m).count());
            for (i, m) in mask.iter().enumerate() { prop_assert_eq!(*m, a[i] != b[i]); }
        }
        let l1 = make_undo(Some(&a), Some(&b));
        let l2 = make_undo(Some(&b), Some(&c));
        let back_b = apply_undo(Some(&c), &l2);
        prop_assert_eq!(back_b.as_ref(), Some(&b));
        prop_assert_eq!(apply_undo(back_b.as_deref(), &l1), Some(a));
    }
}
''')))

CH.append(C("4a-c5", M4A, "94-challenge-timestamp-ordering", "build", "Challenge: timestamp ordering", "medium", "stages_4a::s4a_c5",
  ["the basic timestamp-ordering protocol with read and write timestamps per item","what makes an accepted history equal to a serial one"],
  ["logical-clocks-and-timestamps","multi-version-concurrency-control"],
  "`ToItem` in `src/concurrency/timestamp_ordering.rs`: one data item under **basic timestamp ordering**. Each transaction has a timestamp fixed at begin; the item remembers the largest timestamp that read it (`rts`) and wrote it (`wts`). `read(ts)` aborts when a younger transaction has already written (`ts < wts`); `write(ts, v)` aborts when a younger transaction has already read or written (`ts < rts` or `ts < wts`). Otherwise the operation proceeds and updates the timestamps.",
  "Locking is one way to get serializability; ordering by timestamp is another, with no waiting and no deadlock: a transaction that arrives \"too late\" is simply aborted and restarted with a new timestamp. It is the ancestor of MVCC's read timestamps, and a good place to see what *serial equivalent* means: the order of the timestamps.",
  ["`ToItem::new(initial)`; `read(ts) -> Result<i64, Abort>`; `write(ts, value) -> Result<(), Abort>`.","`read(ts)`: `Err` if `ts < wts`, else `rts = max(rts, ts)` and the current value.","`write(ts, v)`: `Err` if `ts < rts` or `ts < wts`, else `wts = ts` and the value is set.","A refused operation changes nothing."],
  ["`rts` and `wts` never decrease.","The current value is the value written by the accepted write with the largest timestamp (or the initial value)."],
  ["Every accepted read returned the value of the accepted write with the largest timestamp not greater than the reader's.","Running the accepted operations in timestamp order gives the same results (the serial equivalent).","A transaction with a timestamp larger than all others is never aborted."],
  ["write(5, 1); read(3) -> abort; read(7) -> 1; write(6, 2) -> abort (7 has read); write(8, 3) ok"],
  ["The four abort cases and the accepted ones.","Refused operations leave no trace.","A property: accepted reads see the right version in a serial replay."],
  src=("src/concurrency/timestamp_ordering.rs", '''
//! One item under basic timestamp ordering.

#[derive(Debug, PartialEq, Eq)]
pub struct Abort;

pub struct ToItem {
    // @begin 4a-c5
    value: i64,
    rts: u64,
    wts: u64,
    //~ _item: (),
    // @end
}

impl ToItem {
    pub fn new(initial: i64) -> ToItem {
        // @begin 4a-c5
        ToItem { value: initial, rts: 0, wts: 0 }
        //~ todo!("4a-c5: an item nobody has touched")
        // @end
    }

    pub fn read(&mut self, ts: u64) -> Result<i64, Abort> {
        // @begin 4a-c5
        if ts < self.wts {
            return Err(Abort);
        }
        self.rts = self.rts.max(ts);
        Ok(self.value)
        //~ todo!("4a-c5: refuse a read that is older than the last write; otherwise note it")
        // @end
    }

    pub fn write(&mut self, ts: u64, value: i64) -> Result<(), Abort> {
        // @begin 4a-c5
        if ts < self.rts || ts < self.wts {
            return Err(Abort);
        }
        self.wts = ts;
        self.value = value;
        Ok(())
        //~ todo!("4a-c5: refuse a write that is older than a later read or write; otherwise apply it")
        // @end
    }

    pub fn timestamps(&self) -> (u64, u64) {
        // @begin 4a-c5
        (self.rts, self.wts)
        //~ todo!("4a-c5: (read timestamp, write timestamp)")
        // @end
    }
}
'''),
  test=("tests/stages_4a.rs", '''
use bustub::concurrency::timestamp_ordering::{Abort, ToItem};

#[test]
fn s4a_c5_a_read_that_arrives_after_a_younger_write_aborts() {
    let mut i = ToItem::new(0);
    assert_eq!(i.write(5, 1), Ok(()));
    assert_eq!(i.read(3), Err(Abort));
    assert_eq!(i.read(5), Ok(1));
    assert_eq!(i.read(7), Ok(1));
}

#[test]
fn s4a_c5_a_write_that_arrives_after_a_younger_read_aborts() {
    let mut i = ToItem::new(0);
    i.read(7).unwrap();
    assert_eq!(i.write(6, 2), Err(Abort));
    assert_eq!(i.write(8, 3), Ok(()));
    assert_eq!(i.read(9), Ok(3));
}

#[test]
fn s4a_c5_a_write_older_than_the_last_write_aborts() {
    let mut i = ToItem::new(0);
    i.write(5, 1).unwrap();
    assert_eq!(i.write(4, 2), Err(Abort));
    assert_eq!(i.read(6), Ok(1));
}

#[test]
fn s4a_c5_a_refused_operation_changes_nothing() {
    let mut i = ToItem::new(9);
    i.write(5, 1).unwrap();
    let before = i.timestamps();
    let _ = i.read(2);
    let _ = i.write(3, 77);
    assert_eq!(i.timestamps(), before);
    assert_eq!(i.read(5), Ok(1));
}

#[test]
fn s4a_c5_the_largest_timestamp_is_never_refused() {
    let mut i = ToItem::new(0);
    for ts in 1..20 {
        assert!(i.write(ts, ts as i64).is_ok());
        assert_eq!(i.read(ts), Ok(ts as i64));
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: every accepted read returned the value of the accepted write with the largest timestamp not above the reader's.
    #[test]
    fn s4a_c5_property_accepted_reads_match_a_serial_replay(ops in proptest::collection::vec((any::<bool>(), 1u64..8, 0i64..50), 0..40)) {
        let mut item = ToItem::new(-1);
        let mut accepted_writes: Vec<(u64, i64)> = vec![(0, -1)];
        for (is_write, ts, v) in ops {
            if is_write {
                if item.write(ts, v).is_ok() { accepted_writes.push((ts, v)); }
            } else if let Ok(got) = item.read(ts) {
                let want = accepted_writes.iter().filter(|w| w.0 <= ts).max_by_key(|w| w.0).map(|w| w.1);
                prop_assert_eq!(Some(got), want);
            }
            let (r, w) = item.timestamps();
            prop_assert!(accepted_writes.iter().all(|a| a.0 <= w));
            let _ = r;
        }
    }
}
''')))

CH.append(C("4b-c1", M4B, "90-challenge-first-updater-wins", "build", "Challenge: first updater wins", "easy", "stages_4b::s4b_c1",
  ["a write-write conflict detector that never waits","releasing everything a transaction claimed at commit or abort"],
  ["multi-version-concurrency-control","snapshot-isolation"],
  "`WriteClaims` in `src/concurrency/write_claims.rs`: the rule that stops lost updates under snapshot isolation. A transaction **claims** a key before writing it; if another live transaction already holds the claim, the claim fails with the owner's id and the caller aborts (or retries). `release_all(txn)` drops all of a transaction's claims at commit or abort.",
  "Snapshot isolation lets two transactions both read a row and both try to change it; without a rule, the second writer silently overwrites the first (a lost update). \"First updater wins\" is the cheapest rule that prevents it: the first to write a key owns it until it finishes, and the second is refused at once, without blocking.",
  ["`claim(txn, key)` is `Ok(())` if the key is free or already held by `txn`; `Err(Conflict { owner })` if another transaction holds it.","`release_all(txn)` frees every key `txn` holds (returns how many).","`owner_of(key)` is the holder, if any."],
  ["A key has at most one owner.","A transaction's claims all belong to it until it releases them."],
  ["Two transactions can never both succeed in claiming the same key without a release in between.","After `release_all(t)`, no key is owned by `t`.","Claiming the same key twice by the same transaction is the same as once."],
  ["claim(1, 'a') ok; claim(2, 'a') -> conflict with 1; release_all(1); claim(2, 'a') ok"],
  ["Free, own and foreign keys.","Release.","A property against a map."],
  src=("src/concurrency/write_claims.rs", '''
//! Claims on keys for first-updater-wins conflict detection.

use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq)]
pub struct Conflict {
    pub owner: u64,
}

#[derive(Default)]
pub struct WriteClaims {
    // @begin 4b-c1
    owners: HashMap<i64, u64>,
    //~ _claims: (),
    // @end
}

impl WriteClaims {
    pub fn new() -> WriteClaims {
        // @begin 4b-c1
        WriteClaims { owners: HashMap::new() }
        //~ todo!("4b-c1: nothing is claimed")
        // @end
    }

    pub fn claim(&mut self, txn: u64, key: i64) -> Result<(), Conflict> {
        // @begin 4b-c1
        match self.owners.get(&key) {
            Some(&o) if o != txn => Err(Conflict { owner: o }),
            _ => {
                self.owners.insert(key, txn);
                Ok(())
            }
        }
        //~ todo!("4b-c1: take the key if it is free or already yours")
        // @end
    }

    pub fn release_all(&mut self, txn: u64) -> usize {
        // @begin 4b-c1
        let before = self.owners.len();
        self.owners.retain(|_, o| *o != txn);
        before - self.owners.len()
        //~ todo!("4b-c1: free every key the transaction holds")
        // @end
    }

    pub fn owner_of(&self, key: i64) -> Option<u64> {
        // @begin 4b-c1
        self.owners.get(&key).copied()
        //~ todo!("4b-c1: who holds the key")
        // @end
    }
}
'''),
  test=("tests/stages_4b.rs", '''
use bustub::concurrency::write_claims::{Conflict, WriteClaims};
use std::collections::HashMap;

#[test]
fn s4b_c1_the_first_claimant_wins_and_the_second_is_told_who() {
    let mut c = WriteClaims::new();
    assert_eq!(c.claim(1, 10), Ok(()));
    assert_eq!(c.claim(2, 10), Err(Conflict { owner: 1 }));
    assert_eq!(c.owner_of(10), Some(1));
}

#[test]
fn s4b_c1_claiming_your_own_key_again_is_fine() {
    let mut c = WriteClaims::new();
    c.claim(1, 10).unwrap();
    assert_eq!(c.claim(1, 10), Ok(()));
    assert_eq!(c.release_all(1), 1);
}

#[test]
fn s4b_c1_release_frees_everything_the_transaction_held_and_nothing_else() {
    let mut c = WriteClaims::new();
    for k in [1, 2, 3] {
        c.claim(1, k).unwrap();
    }
    c.claim(2, 4).unwrap();
    assert_eq!(c.release_all(1), 3);
    assert_eq!((c.owner_of(1), c.owner_of(4)), (None, Some(2)));
    assert_eq!(c.claim(2, 1), Ok(()), "a released key can be claimed by another");
    assert_eq!(c.release_all(9), 0);
}

#[test]
fn s4b_c1_a_conflict_changes_neither_the_owner_nor_the_losers_claims() {
    let mut c = WriteClaims::new();
    c.claim(1, 10).unwrap();
    assert!(c.claim(2, 10).is_err());
    assert_eq!(c.owner_of(10), Some(1));
    assert_eq!(c.release_all(2), 0, "the loser holds nothing");
    assert_eq!(c.release_all(1), 1);
    assert_eq!(c.owner_of(10), None);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a map from key to owner.
    #[test]
    fn s4b_c1_property_claims_match_an_owner_map(ops in proptest::collection::vec((any::<bool>(), 1u64..4, 0i64..5), 0..40)) {
        let mut c = WriteClaims::new();
        let mut m: HashMap<i64, u64> = HashMap::new();
        for (claim, txn, key) in ops {
            if claim {
                let want = match m.get(&key) { Some(&o) if o != txn => Err(Conflict { owner: o }), _ => { m.insert(key, txn); Ok(()) } };
                prop_assert_eq!(c.claim(txn, key), want);
            } else {
                let n = m.values().filter(|&&o| o == txn).count();
                m.retain(|_, o| *o != txn);
                prop_assert_eq!(c.release_all(txn), n);
            }
            for k in 0..5 { prop_assert_eq!(c.owner_of(k), m.get(&k).copied()); }
        }
    }
}
''')))

CH.append(C("4b-c2", M4B, "91-challenge-a-snapshot-isolation-checker", "build", "Challenge: a snapshot-isolation checker", "hard", "stages_4b::s4b_c2",
  ["checking a recorded history against the definition of snapshot isolation","separating a wrong read from a lost update"],
  ["snapshot-isolation","serializable-validation-by-predicates","model-based-testing"],
  "`check_si` in `src/concurrency/si_checker.rs`: given a history of **committed** transactions, each with a start timestamp, a commit timestamp, the values it read (key and value) and the values it wrote (key and value), decide whether the history is valid snapshot isolation. Two rules: every read returns the value written by the latest transaction that committed **at or before the reader's start** (or the reader's own earlier write, or the initial value 0); and no two transactions whose lifetimes overlap wrote the same key (first committer wins).",
  "A database that claims snapshot isolation is checked the way Jepsen checks it: run a workload, record what every transaction saw, and verify the history against the definition. The definition is exactly these two rules, and a checker for them is how you find an engine that returns a stale read or admits a lost update.",
  ["`Txn { id, start, commit, reads: Vec<(key, value)>, writes: Vec<(key, value)> }`; timestamps are distinct; `start < commit`. The initial value of every key is 0.","`check_si(history) -> Result<(), Violation>` with `Violation::StaleRead { txn, key }` (a read that is not the snapshot value) or `Violation::LostUpdate { a, b, key }` (overlapping writers of one key, `a` before `b` in commit order).","Reads of a key the transaction already wrote earlier see its own last write; the checker takes a transaction's reads as happening in listed order **before** its writes."],
  ["A history accepted by the checker has, for every read, exactly one defensible source: the latest committed write at the start, or the initial value.","Violations are reported deterministically: the earliest transaction in commit order that is wrong."],
  ["Removing a transaction that only reads can never create a violation.","A serial history (no overlaps) with correct reads is always valid.","Changing the value of one read in a valid history that has a different snapshot value makes it invalid."],
  ["T1 [1,3] writes x=1; T2 [2,4] reads x -> 0 (snapshot at 2, T1 not committed yet): valid","T2 reads x -> 1: StaleRead? no: that is a read of an uncommitted/not-yet-visible value -> violation"],
  ["Valid histories: serial and concurrent.","A stale or future read.","A lost update by overlapping writers.","A property: a history generated by a correct SI engine is valid, and corrupting a read breaks it."],
  src=("src/concurrency/si_checker.rs", '''
//! Checking a history against snapshot isolation.

#[derive(Debug, Clone)]
pub struct Txn {
    pub id: u32,
    pub start: u64,
    pub commit: u64,
    pub reads: Vec<(i64, i64)>,
    pub writes: Vec<(i64, i64)>,
}

#[derive(Debug, PartialEq, Eq)]
pub enum Violation {
    StaleRead { txn: u32, key: i64 },
    LostUpdate { a: u32, b: u32, key: i64 },
}

pub fn check_si(history: &[Txn]) -> Result<(), Violation> {
    // @begin 4b-c2
    let mut order: Vec<&Txn> = history.iter().collect();
    order.sort_by_key(|t| t.commit);
    for (i, t) in order.iter().enumerate() {
        for &(key, value) in &t.reads {
            // the snapshot value: the latest write committed at or before `start` (the sort is by commit time)
            let snapshot = order
                .iter()
                .filter(|o| o.commit <= t.start && o.id != t.id)
                .rev()
                .find_map(|o| o.writes.iter().rev().find(|w| w.0 == key).map(|w| w.1))
                .unwrap_or(0);
            if snapshot != value {
                return Err(Violation::StaleRead { txn: t.id, key });
            }
        }
        for later in &order[i + 1..] {
            // `later` committed after `t`: they overlap when `later` started before `t` committed
            if later.start < t.commit {
                if let Some(&(key, _)) = t.writes.iter().find(|w| later.writes.iter().any(|x| x.0 == w.0)) {
                    return Err(Violation::LostUpdate { a: t.id, b: later.id, key });
                }
            }
        }
    }
    Ok(())
    //~ todo!("4b-c2: check every read against the snapshot at its start, then overlapping writers of the same key")
    // @end
}
'''),
  test=("tests/stages_4b.rs", '''
use bustub::concurrency::si_checker::{check_si, Txn, Violation::*};

fn t(id: u32, start: u64, commit: u64, reads: &[(i64, i64)], writes: &[(i64, i64)]) -> Txn {
    Txn { id, start, commit, reads: reads.to_vec(), writes: writes.to_vec() }
}

#[test]
fn s4b_c2_a_reader_that_started_before_a_commit_does_not_see_it() {
    let h = [t(1, 1, 3, &[], &[(0, 1)]), t(2, 2, 4, &[(0, 0)], &[])];
    assert_eq!(check_si(&h), Ok(()));
}

#[test]
fn s4b_c2_a_reader_that_started_after_a_commit_must_see_it() {
    let h = [t(1, 1, 2, &[], &[(0, 1)]), t(2, 3, 4, &[(0, 1)], &[])];
    assert_eq!(check_si(&h), Ok(()));
    let stale = [t(1, 1, 2, &[], &[(0, 1)]), t(2, 3, 4, &[(0, 0)], &[])];
    assert_eq!(check_si(&stale), Err(StaleRead { txn: 2, key: 0 }));
}

#[test]
fn s4b_c2_reading_a_value_that_was_not_yet_committed_is_a_violation() {
    let h = [t(1, 1, 4, &[], &[(0, 1)]), t(2, 2, 5, &[(0, 1)], &[])];
    assert_eq!(check_si(&h), Err(StaleRead { txn: 2, key: 0 }));
}

#[test]
fn s4b_c2_overlapping_writers_of_one_key_are_a_lost_update() {
    let h = [t(1, 1, 4, &[(0, 0)], &[(0, 5)]), t(2, 2, 5, &[(0, 0)], &[(0, 7)])];
    assert_eq!(check_si(&h), Err(LostUpdate { a: 1, b: 2, key: 0 }));
}

#[test]
fn s4b_c2_writers_of_one_key_that_do_not_overlap_are_fine() {
    let h = [t(1, 1, 2, &[(0, 0)], &[(0, 5)]), t(2, 3, 4, &[(0, 5)], &[(0, 7)])];
    assert_eq!(check_si(&h), Ok(()));
}

#[test]
fn s4b_c2_write_skew_is_allowed_by_snapshot_isolation() {
    // both read x and y = 0, then write different keys: legal under SI, an anomaly under serializability
    let h = [t(1, 1, 3, &[(0, 0), (1, 0)], &[(0, 1)]), t(2, 2, 4, &[(0, 0), (1, 0)], &[(1, 1)])];
    assert_eq!(check_si(&h), Ok(()));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: histories produced by a model SI engine are valid; changing one read makes them invalid.
    #[test]
    fn s4b_c2_property_engine_histories_are_valid_and_corrupted_ones_are_not(plan in proptest::collection::vec((0u64..3, 0i64..3, any::<bool>(), 1i64..9), 1..8)) {
        // run transactions one after another but let each start a little before the previous commit (overlap by `gap`)
        let mut store: std::collections::HashMap<i64, Vec<(u64, i64)>> = Default::default();
        let mut hist: Vec<Txn> = Vec::new();
        let mut clock = 10u64;
        let mut claimed: Vec<(u64, u64, i64)> = Vec::new(); // (start, commit, key) of committed writers
        for (id, (gap, key, writes, val)) in plan.into_iter().enumerate() {
            let start = clock.saturating_sub(gap).max(1);
            let commit = clock + 5;
            // first committer wins: skip a writer that overlaps an earlier committed writer of the same key
            let do_write = writes && !claimed.iter().any(|&(_, c, k)| k == key && c > start);
            let snapshot = store.get(&key).and_then(|v| v.iter().rev().find(|&&(c, _)| c <= start).map(|&(_, x)| x)).unwrap_or(0);
            let t = Txn { id: id as u32, start, commit, reads: vec![(key, snapshot)], writes: if do_write { vec![(key, val)] } else { vec![] } };
            if do_write { store.entry(key).or_default().push((commit, val)); claimed.push((start, commit, key)); }
            hist.push(t);
            clock += 10;
        }
        prop_assert_eq!(check_si(&hist), Ok(()));
        let mut bad = hist.clone();
        let last = bad.len() - 1;
        let original = bad[last].reads[0].1;
        bad[last].reads[0].1 = original + 100;
        prop_assert!(check_si(&bad).is_err());
    }
}
''')))

CH.append(C("4b-c3", M4B, "92-challenge-the-version-gc-dropped", "debug", "Challenge: the version nobody can see", "easy", "stages_4b::s4b_c3",
  ["finding a garbage-collection bug that removes a version a reader still needs"],
  ["multi-version-concurrency-control","snapshot-isolation","property-testing-and-fuzzing"],
  "`gc_chain` in `src/concurrency/version_gc.rs` removes the versions of one row that no transaction can read any more, given the **watermark**: the smallest read timestamp of any active transaction. It looks right, and after a collection a reader at the watermark gets the wrong value. Find the bug and fix it.",
  "A version is garbage only if no reader, now or later, can pick it. The subtle one is the newest version at or below the watermark: it is the *oldest* version a reader at the watermark may still need, so it must stay, and everything older goes. Dropping it as well produces a database that works until the one transaction that held back the watermark reads.",
  ["`chain` lists `(commit_ts, value)` **newest first**. `gc_chain(chain, watermark)` keeps every version with `commit_ts > watermark` and the single newest version with `commit_ts <= watermark`; everything older is removed.","Returns the number of versions removed."],
  ["For every read timestamp `t >= watermark`, reading the chain gives the same answer before and after.","The chain is still newest first, with strictly decreasing timestamps."],
  ["A second collection with the same watermark removes nothing.","A higher watermark never keeps more versions.","The chain never ends up empty if it was not empty."],
  ["[(9,c),(5,b),(2,a)], watermark 6 -> keeps (9,c),(5,b); removes (2,a)"],
  ["Watermark between, below and above the versions.","Idempotence.","A property: reads at or above the watermark are unchanged."],
  src=("src/concurrency/version_gc.rs", '''
//! Garbage collection of one row's version chain.

/// `chain` is `(commit_ts, value)` newest first. Removes what no reader at or above `watermark` can see; returns how many versions went.
pub fn gc_chain(chain: &mut Vec<(u64, i64)>, watermark: u64) -> usize {
    let before = chain.len();
    // @begin 4b-c3
    // the first version (newest first) at or below the watermark is the newest one a reader at the watermark can see: keep it, drop the rest
    match chain.iter().position(|&(ts, _)| ts <= watermark) {
        Some(i) => chain.truncate(i + 1),
        None => {}
    }
    //~ chain.retain(|&(ts, _)| ts > watermark);
    // @end
    before - chain.len()
}

/// The value a reader with timestamp `read_ts` sees.
pub fn read_at(chain: &[(u64, i64)], read_ts: u64) -> Option<i64> {
    chain.iter().find(|&&(ts, _)| ts <= read_ts).map(|&(_, v)| v)
}
'''),
  test=("tests/stages_4b.rs", '''
use bustub::concurrency::version_gc::{gc_chain, read_at};

#[test]
fn s4b_c3_the_newest_version_at_or_below_the_watermark_stays() {
    let mut c = vec![(9, 30), (5, 20), (2, 10)];
    assert_eq!(gc_chain(&mut c, 6), 1);
    assert_eq!(c, vec![(9, 30), (5, 20)]);
    assert_eq!(read_at(&c, 6), Some(20), "a reader at the watermark still reads version 5");
}

#[test]
fn s4b_c3_a_watermark_exactly_on_a_version_keeps_that_version() {
    let mut c = vec![(9, 30), (5, 20), (2, 10)];
    gc_chain(&mut c, 5);
    assert_eq!(c, vec![(9, 30), (5, 20)]);
}

#[test]
fn s4b_c3_a_watermark_below_everything_removes_nothing() {
    let mut c = vec![(9, 30), (5, 20)];
    assert_eq!(gc_chain(&mut c, 1), 0);
    assert_eq!(c.len(), 2);
}

#[test]
fn s4b_c3_a_watermark_above_everything_keeps_only_the_newest() {
    let mut c = vec![(9, 30), (5, 20), (2, 10)];
    assert_eq!(gc_chain(&mut c, 100), 2);
    assert_eq!(c, vec![(9, 30)]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: every read at or above the watermark is unchanged, and collecting again removes nothing.
    #[test]
    fn s4b_c3_property_readers_at_or_above_the_watermark_are_unaffected(stamps in proptest::collection::btree_set(1u64..30, 0..8), watermark in 0u64..32) {
        let mut chain: Vec<(u64, i64)> = stamps.iter().rev().map(|&t| (t, t as i64 * 10)).collect();
        let before = chain.clone();
        gc_chain(&mut chain, watermark);
        for t in watermark..40 {
            prop_assert_eq!(read_at(&chain, t), read_at(&before, t), "read at {}", t);
        }
        prop_assert!(chain.windows(2).all(|w| w[0].0 > w[1].0));
        prop_assert_eq!(gc_chain(&mut chain, watermark), 0);
        if !before.is_empty() { prop_assert!(!chain.is_empty()); }
    }
}
''')))

CH.append(C("4b-c4", M4B, "93-challenge-predicate-validation", "build", "Challenge: predicate validation", "medium", "stages_4b::s4b_c4",
  ["detecting read-write conflicts for range and equality predicates, not only for single rows","checking both the old and the new image of a write"],
  ["serializable-validation-by-predicates","snapshot-isolation","conjunctive-predicates"],
  "`validate` in `src/concurrency/predicate_validation.rs`: a serializable transaction remembers the **predicates** it read with (`a = 5`, `a BETWEEN 10 AND 20`). At commit, it checks every write made by transactions that committed since its snapshot: if the old row or the new row of a write satisfies one of its predicates, the write could have changed what the predicate returned, and the transaction must abort.",
  "Locking rows misses *phantoms*: a row inserted by someone else that your range query would have returned. Validating predicates catches them, and the subtle part is the two images: a write that *moves* a row out of your range (old image matches) matters as much as one that moves it in (new image matches).",
  ["`Pred::Eq(col, v)` and `Pred::Range(col, lo, hi)` (inclusive); a row is a slice of `i64`.","`Write { old: Option<Vec<i64>>, new: Option<Vec<i64>> }` (insert has no `old`, delete has no `new`).","`validate(preds, writes)` is `true` (no conflict) iff **no** write has an image (old or new) that satisfies any predicate."],
  ["Order of predicates and writes does not matter.","A write with no images (both `None`) conflicts with nothing."],
  ["Adding a predicate or a write can only turn `true` into `false`.","A write that does not touch the predicate columns' values (both images equal and outside) never conflicts.","An insert into the range conflicts; a delete from the range conflicts; an update from outside to outside does not."],
  ["pred a in [10,20]: insert row [15] -> conflict; update [5] -> [8] -> fine; update [15] -> [30] -> conflict"],
  ["Equality and range predicates; each image.","No predicates and no writes.","A property against a brute-force check."],
  src=("src/concurrency/predicate_validation.rs", '''
//! Validating a serializable transaction's predicate reads against later writes.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Pred {
    Eq(usize, i64),
    Range(usize, i64, i64),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Write {
    pub old: Option<Vec<i64>>,
    pub new: Option<Vec<i64>>,
}

fn matches(p: &Pred, row: &[i64]) -> bool {
    match p {
        Pred::Eq(c, v) => row.get(*c) == Some(v),
        Pred::Range(c, lo, hi) => row.get(*c).is_some_and(|x| lo <= x && x <= hi),
    }
}

/// True when no write could have changed what any predicate returned.
pub fn validate(preds: &[Pred], writes: &[Write]) -> bool {
    // @begin 4b-c4
    !writes.iter().any(|w| {
        [&w.old, &w.new].into_iter().flatten().any(|row| preds.iter().any(|p| matches(p, row)))
    })
    //~ todo!("4b-c4: a write conflicts when its old or its new row satisfies a predicate")
    // @end
}
'''),
  test=("tests/stages_4b.rs", '''
use bustub::concurrency::predicate_validation::{validate, Pred, Write};

fn w(old: Option<&[i64]>, new: Option<&[i64]>) -> Write {
    Write { old: old.map(|r| r.to_vec()), new: new.map(|r| r.to_vec()) }
}

#[test]
fn s4b_c4_an_insert_into_the_range_is_a_phantom() {
    assert!(!validate(&[Pred::Range(0, 10, 20)], &[w(None, Some(&[15]))]));
    assert!(validate(&[Pred::Range(0, 10, 20)], &[w(None, Some(&[25]))]));
}

#[test]
fn s4b_c4_a_delete_from_the_range_matters_too() {
    assert!(!validate(&[Pred::Range(0, 10, 20)], &[w(Some(&[15]), None)]));
}

#[test]
fn s4b_c4_an_update_matters_when_either_image_is_in_the_range() {
    let p = [Pred::Range(0, 10, 20)];
    assert!(validate(&p, &[w(Some(&[5]), Some(&[8]))]), "outside to outside");
    assert!(!validate(&p, &[w(Some(&[15]), Some(&[30]))]), "moved out of the range");
    assert!(!validate(&p, &[w(Some(&[5]), Some(&[12]))]), "moved into the range");
}

#[test]
fn s4b_c4_equality_predicates_and_other_columns() {
    assert!(!validate(&[Pred::Eq(1, 7)], &[w(None, Some(&[0, 7]))]));
    assert!(validate(&[Pred::Eq(1, 7)], &[w(None, Some(&[7, 0]))]), "the value is in another column");
}

#[test]
fn s4b_c4_nothing_to_check_is_valid() {
    assert!(validate(&[], &[w(None, Some(&[1]))]));
    assert!(validate(&[Pred::Eq(0, 1)], &[]));
    assert!(validate(&[Pred::Eq(0, 1)], &[w(None, None)]));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: monotone in the predicates and the writes, and equal to a brute-force check.
    #[test]
    fn s4b_c4_property_conflicts_are_monotone(preds in proptest::collection::vec((0usize..2, 0i64..6, 0i64..6), 0..4), writes in proptest::collection::vec((proptest::option::of((0i64..8, 0i64..8)), proptest::option::of((0i64..8, 0i64..8))), 0..5)) {
        let ps: Vec<Pred> = preds.iter().map(|&(c, a, b)| if a == b { Pred::Eq(c, a) } else { Pred::Range(c, a.min(b), a.max(b)) }).collect();
        let ws: Vec<Write> = writes.iter().map(|(o, n)| Write { old: o.map(|(a, b)| vec![a, b]), new: n.map(|(a, b)| vec![a, b]) }).collect();
        let brute = ws.iter().all(|w| [&w.old, &w.new].into_iter().flatten().all(|r| ps.iter().all(|p| match p { Pred::Eq(c, v) => r[*c] != *v, Pred::Range(c, lo, hi) => !(*lo <= r[*c] && r[*c] <= *hi) })));
        prop_assert_eq!(validate(&ps, &ws), brute);
        if !validate(&ps[..ps.len().saturating_sub(1)], &ws) { prop_assert!(!validate(&ps, &ws)); }
    }
}
''')))

CH.append(C("4b-c5", M4B, "94-challenge-savepoints", "build", "Challenge: savepoints", "medium", "stages_4b::s4b_c5",
  ["partial rollback with an undo stack","what rolling back to a savepoint invalidates"],
  ["rolling-back-with-undo-logs","multi-version-concurrency-control"],
  "`SavepointTxn` in `src/concurrency/savepoints.rs`: a transaction over a `BTreeMap<i64, i64>` with `set(k, v)`, `delete(k)`, `savepoint()` (returns an id), `rollback_to(id)` (undo everything done after the savepoint, keeping the transaction open), `release(id)` and `commit()` (returns the final map). Undo is done by keeping, for every change, what was there before.",
  "`SAVEPOINT` is how a client retries part of a transaction after a constraint violation without losing the rest, and how a stored procedure with an exception handler undoes just its own work. It needs the same undo information as a full abort, used selectively: roll back to a mark, drop the marks above it, and leave the transaction running.",
  ["`savepoint()` returns an increasing id. `rollback_to(id)` restores the state at that savepoint and removes every savepoint created after it (the savepoint itself stays usable). `release(id)` forgets the savepoint and all after it (their changes stay).","An unknown or already released id is `Err(NoSuchSavepoint)` and changes nothing.","`rollback_all()` restores the state at the start of the transaction; `commit()` returns the current map."],
  ["After `rollback_to(id)` the map equals the map at the moment `savepoint()` returned `id`.","Savepoint ids are never reused."],
  ["`savepoint(); changes...; rollback_to` leaves no trace of the changes.","Nested savepoints roll back independently, innermost first.","The final map equals replaying only the changes that were not rolled back."],
  ["set 1=1; sp A; set 1=2; sp B; set 2=9; rollback_to A -> {1: 1}; B is gone"],
  ["Set, delete, rollback, nested savepoints.","Releasing and unknown ids.","A property against full snapshots."],
  src=("src/concurrency/savepoints.rs", '''
//! Savepoints over a map, by undo records.

use std::collections::BTreeMap;

#[derive(Debug, PartialEq, Eq)]
pub struct NoSuchSavepoint;

pub struct SavepointTxn {
    // @begin 4b-c5
    data: BTreeMap<i64, i64>,
    /// For each change, the previous state of the key (`None`: it was absent).
    undo: Vec<(i64, Option<i64>)>,
    /// (savepoint id, length of `undo` when it was taken), oldest first.
    marks: Vec<(u64, usize)>,
    next_id: u64,
    //~ _txn: (),
    // @end
}

impl SavepointTxn {
    pub fn begin(initial: BTreeMap<i64, i64>) -> SavepointTxn {
        // @begin 4b-c5
        SavepointTxn { data: initial, undo: Vec::new(), marks: Vec::new(), next_id: 1 }
        //~ todo!("4b-c5: a transaction over the initial data with nothing to undo")
        // @end
    }

    pub fn set(&mut self, key: i64, value: i64) {
        // @begin 4b-c5
        let old = self.data.insert(key, value);
        self.undo.push((key, old));
        //~ todo!("4b-c5: remember what the key was, then write")
        // @end
    }

    pub fn delete(&mut self, key: i64) {
        // @begin 4b-c5
        let old = self.data.remove(&key);
        self.undo.push((key, old));
        //~ todo!("4b-c5: remember what the key was, then remove")
        // @end
    }

    pub fn get(&self, key: i64) -> Option<i64> {
        // @begin 4b-c5
        self.data.get(&key).copied()
        //~ todo!("4b-c5: the current value")
        // @end
    }

    pub fn savepoint(&mut self) -> u64 {
        // @begin 4b-c5
        let id = self.next_id;
        self.next_id += 1;
        self.marks.push((id, self.undo.len()));
        id
        //~ todo!("4b-c5: mark the current end of the undo log")
        // @end
    }

    pub fn rollback_to(&mut self, id: u64) -> Result<(), NoSuchSavepoint> {
        // @begin 4b-c5
        let at = self.marks.iter().position(|m| m.0 == id).ok_or(NoSuchSavepoint)?;
        let keep = self.marks[at].1;
        while self.undo.len() > keep {
            let (key, old) = self.undo.pop().unwrap();
            match old {
                Some(v) => {
                    self.data.insert(key, v);
                }
                None => {
                    self.data.remove(&key);
                }
            }
        }
        self.marks.truncate(at + 1);
        Ok(())
        //~ todo!("4b-c5: undo back to the mark, newest first; drop the later savepoints")
        // @end
    }

    pub fn release(&mut self, id: u64) -> Result<(), NoSuchSavepoint> {
        // @begin 4b-c5
        let at = self.marks.iter().position(|m| m.0 == id).ok_or(NoSuchSavepoint)?;
        self.marks.truncate(at);
        Ok(())
        //~ todo!("4b-c5: forget the savepoint and every later one, keeping their changes")
        // @end
    }

    pub fn rollback_all(&mut self) {
        // @begin 4b-c5
        while let Some((key, old)) = self.undo.pop() {
            match old {
                Some(v) => {
                    self.data.insert(key, v);
                }
                None => {
                    self.data.remove(&key);
                }
            }
        }
        self.marks.clear();
        //~ todo!("4b-c5: undo everything")
        // @end
    }

    pub fn commit(self) -> BTreeMap<i64, i64> {
        // @begin 4b-c5
        self.data
        //~ todo!("4b-c5: the final map")
        // @end
    }
}
'''),
  test=("tests/stages_4b.rs", '''
use bustub::concurrency::savepoints::{NoSuchSavepoint, SavepointTxn};
use std::collections::BTreeMap;

#[test]
fn s4b_c5_rolling_back_to_a_savepoint_undoes_what_came_after_it() {
    let mut t = SavepointTxn::begin(BTreeMap::new());
    t.set(1, 1);
    let a = t.savepoint();
    t.set(1, 2);
    t.set(2, 9);
    t.delete(1);
    assert_eq!(t.rollback_to(a), Ok(()));
    assert_eq!((t.get(1), t.get(2)), (Some(1), None));
    assert_eq!(t.commit(), BTreeMap::from([(1, 1)]));
}

#[test]
fn s4b_c5_a_later_savepoint_disappears_when_an_earlier_one_is_rolled_back_to() {
    let mut t = SavepointTxn::begin(BTreeMap::new());
    let a = t.savepoint();
    t.set(1, 1);
    let b = t.savepoint();
    t.set(2, 2);
    t.rollback_to(a).unwrap();
    assert_eq!(t.rollback_to(b), Err(NoSuchSavepoint));
    assert_eq!(t.rollback_to(a), Ok(()), "the savepoint itself can be used again");
    assert_eq!(t.commit(), BTreeMap::new());
}

#[test]
fn s4b_c5_nested_savepoints_roll_back_innermost_first() {
    let mut t = SavepointTxn::begin(BTreeMap::from([(1, 10)]));
    let a = t.savepoint();
    t.set(1, 20);
    let b = t.savepoint();
    t.set(1, 30);
    t.rollback_to(b).unwrap();
    assert_eq!(t.get(1), Some(20));
    t.rollback_to(a).unwrap();
    assert_eq!(t.get(1), Some(10));
}

#[test]
fn s4b_c5_release_keeps_the_changes_but_forgets_the_marks() {
    let mut t = SavepointTxn::begin(BTreeMap::new());
    let a = t.savepoint();
    t.set(1, 1);
    let b = t.savepoint();
    t.set(2, 2);
    assert_eq!(t.release(a), Ok(()));
    assert_eq!(t.rollback_to(b), Err(NoSuchSavepoint), "releasing a savepoint releases the later ones too");
    assert_eq!(t.release(99), Err(NoSuchSavepoint));
    assert_eq!(t.commit(), BTreeMap::from([(1, 1), (2, 2)]));
}

#[test]
fn s4b_c5_rolling_back_everything_restores_the_initial_state() {
    let init = BTreeMap::from([(1, 1), (2, 2)]);
    let mut t = SavepointTxn::begin(init.clone());
    t.set(1, 5);
    t.delete(2);
    t.set(3, 3);
    t.rollback_all();
    assert_eq!(t.commit(), init);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: rolling back to a savepoint gives exactly the map as it was when the savepoint was taken.
    #[test]
    fn s4b_c5_property_rollback_equals_a_snapshot(ops in proptest::collection::vec((0u8..4, 0i64..4, 0i64..9), 0..40)) {
        let mut t = SavepointTxn::begin(BTreeMap::new());
        let mut model: BTreeMap<i64, i64> = BTreeMap::new();
        let mut snaps: Vec<(u64, BTreeMap<i64, i64>)> = Vec::new();
        for (op, k, v) in ops {
            match op {
                0 => { t.set(k, v); model.insert(k, v); }
                1 => { t.delete(k); model.remove(&k); }
                2 => { let id = t.savepoint(); snaps.push((id, model.clone())); }
                _ => {
                    if let Some(pos) = snaps.len().checked_sub(1).map(|n| (v as usize) % (n + 1)).filter(|&p| p < snaps.len()) {
                        let (id, snap) = snaps[pos].clone();
                        prop_assert_eq!(t.rollback_to(id), Ok(()));
                        model = snap;
                        snaps.truncate(pos + 1);
                    }
                }
            }
            for key in 0..4 { prop_assert_eq!(t.get(key), model.get(&key).copied()); }
        }
        prop_assert_eq!(t.commit(), model);
    }
}
''')))
