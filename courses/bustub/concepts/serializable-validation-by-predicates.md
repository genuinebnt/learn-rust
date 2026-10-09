---
title: Serializable validation: checking that nothing you read has changed
summary: How a database that runs on snapshots catches write skew: remember the predicates a transaction scanned with, and at commit check whether a transaction that committed meanwhile changed anything those predicates match.
minutes: 8
---
Snapshot isolation (see *snapshot isolation*) lets two transactions read the same snapshot and write different rows, which can break an invariant that no serial order would. **Serializable** isolation closes that gap without going back to locking readers. The approach of the HyPer paper, which BusTub follows:

> A transaction is serializable if, at commit, **nothing it read has been changed by a transaction that committed since it began.**

If that holds, the transaction would have seen the same data had it run at its commit time instead of its start time, so running it "at the time of its snapshot" and "at the time of its commit" are the same, and the order of commits is a valid serial order.

## What "read" means: predicates, not rows

Checking the rows a transaction touched is not enough: a *phantom* is a row that did **not** exist when the transaction scanned (`WHERE a = 0`) and was inserted, or changed to match, by someone else. So the transaction remembers its **scan predicates**: for each scan, the table and the filter it used (a full scan remembers "true"). A scan that read through an index point lookup remembers the lookup's predicate too.

## The commit-time check

At commit, for a serializable transaction `T` that wrote something:

1. Find the transactions that committed after `T` began: `commit_ts > T.read_ts`.
2. For each, for each tuple it wrote (its write set), build two versions: the one **just before** its commit (as of `commit_ts - 1`) and the one **at** its commit (as of `commit_ts`). The first may not exist (an insert) and so may the second (a delete). Reconstruct each with the undo logs, as a reader at that timestamp would.
3. If **any** of `T`'s predicates on that table evaluates to true on either version, `T` read something that changed: `T` fails validation and is aborted; `commit` returns `false`.

A transaction that wrote nothing needs no check: it only read its snapshot, which is consistent, and can be serialised at its read timestamp.

```svg
caption: Two serializable transactions swap values. T3 scanned a = 0, then T2 committed a change to rows that match a = 0 (before: a = 1, after: a = 0). When T3 commits, validation finds the match and aborts it. T2 committed first, so it wins.
<svg viewBox="0 0 760 170" role="img" aria-label="Timeline of two transactions where the second fails validation">
<line class="ln" x1="30" y1="95" x2="730" y2="95"/>
<text class="mid dim sm" x="80" y="120">T2, T3 begin (read ts 1)</text><circle cx="80" cy="95" r="5" style="fill:var(--dim)"/>
<text class="mid fg sm" x="260" y="70">T3 scans a = 0</text><circle cx="260" cy="95" r="5" style="fill:var(--accent, #4a8)"/>
<text class="mid fg sm" x="440" y="70">T2 commits at 2</text><circle cx="440" cy="95" r="5" style="fill:var(--dim)"/>
<text class="mid t-b sm" x="620" y="70">T3 commits: aborted</text><circle cx="620" cy="95" r="5" style="fill:var(--dim)"/>
<text class="mid dim sm" x="530" y="140">T2 wrote rows matching "a = 0"</text>
</svg>
```

## The cost

Validation scans the write sets of recent committers and evaluates each predicate on up to two versions of each tuple: `O(committers × tuples written × predicates)`. A system with long transactions and many writers pays more, and aborts more: the price of serializability without blocking readers. Real systems index predicates or use cheaper conservative checks (PostgreSQL's SSI tracks read-write dependencies instead and may abort spuriously).

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::unordered_map<table_oid_t, std::vector<AbstractExpressionRef>> scan_predicates_` in the transaction | `HashMap<TableOid, Vec<ExprRef>>` behind the transaction's mutex |
| evaluating `pred->Evaluate(&tuple, schema).GetAs<bool>()` | `pred.evaluate(&tuple, schema)?.as_bool() == Some(true)` (NULL is not true) |

**Port rule:** a predicate holds only when it evaluates to `Some(true)`; NULL and false are both "no match".

## In real code

### Using it: validating against a committed write

```rust test
type Row = (i32, i32);

struct Committed {
    commit_ts: i64,
    // (before image, after image) of each tuple the transaction wrote
    writes: Vec<(Option<Row>, Option<Row>)>,
}

fn validates(read_ts: i64, predicates: &[&dyn Fn(&Row) -> bool], committed: &[Committed]) -> bool {
    for c in committed.iter().filter(|c| c.commit_ts > read_ts) {
        for (before, after) in &c.writes {
            for row in [before, after].into_iter().flatten() {
                if predicates.iter().any(|p| p(row)) {
                    return false;
                }
            }
        }
    }
    true
}

#[test]
fn a_change_matching_a_scanned_predicate_fails_validation() {
    let a_is_0 = |r: &Row| r.0 == 0;
    let t2 = Committed { commit_ts: 2, writes: vec![(Some((1, 100)), Some((0, 100)))] };
    assert!(!validates(1, &[&a_is_0], &[t2]), "after-image has a = 0");
}

#[test]
fn unrelated_changes_and_earlier_commits_do_not() {
    let a_is_0 = |r: &Row| r.0 == 0;
    let unrelated = Committed { commit_ts: 2, writes: vec![(Some((5, 1)), Some((6, 1)))] };
    let earlier = Committed { commit_ts: 1, writes: vec![(Some((0, 1)), None)] };
    assert!(validates(1, &[&a_is_0], &[unrelated, earlier]), "ts 1 committed before T began");
}
```

### Using it: inserts and deletes have one image

```rust test
type Row = (i32, i32);

fn matches(p: &dyn Fn(&Row) -> bool, before: Option<Row>, after: Option<Row>) -> bool {
    before.iter().chain(after.iter()).any(|r| p(r))
}

#[test]
fn an_insert_is_seen_through_its_after_image_a_delete_through_its_before_image() {
    let a_is_0 = |r: &Row| r.0 == 0;
    assert!(matches(&a_is_0, None, Some((0, 7))), "a phantom: a new matching row");
    assert!(matches(&a_is_0, Some((0, 7)), None), "a matching row vanished");
    assert!(!matches(&a_is_0, Some((3, 7)), None));
}
```

### In the exercises

- **4b-08:** `verify_txn` and the scan predicates recorded by the scans.
- **4b-09:** BusTub's `SerializableTest` and the concurrent variant (exactly one of two conflicting commits succeeds).

### Where it is used

- **HyPer** (Neumann, Mühlbauer, Kemper, SIGMOD 2015) introduced this precision-locking style validation for MVCC.
- **PostgreSQL** `SERIALIZABLE` uses serializable snapshot isolation (SSI), which tracks read-write dependencies between concurrent transactions rather than predicates, and aborts a transaction that would complete a dangerous cycle.
- **Cockroach and other snapshot-based systems** enforce serializability with different mechanisms (timestamp pushing, read refreshes); the common idea is that a read must still be valid at commit time.
