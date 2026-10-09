---
title: Version chains and undo logs: rebuilding an older tuple
summary: Why a database keeps old versions at all, how BusTub keeps the newest in the table and the older ones as small undo logs, and how a reader walks the chain and applies logs to see exactly the version it is allowed to see.
minutes: 14
---
Imagine a report that starts at 10:00 and scans the whole `accounts` table. It takes four minutes. At 10:01 a customer pays a bill and the row for account 77 changes from a balance of 90 to a balance of 40. Which balance should the report print for account 77?

Whatever answer you choose is a promise about what a transaction is. If the report prints 40, then the report shows a world that did not exist at 10:00 and might be internally inconsistent: the money moved out of one account it has already counted and into another it has not counted yet, and the totals no longer add up. If it prints 90, the report shows one consistent moment, the moment it started, as if everyone else had stood still. That second promise is what **snapshot isolation** gives you, and it is what multi-version concurrency control (MVCC) exists to provide. The price is that the database must still be able to produce the balance of 90 after the row has been overwritten with 40. Somewhere, the old version has to live.

There are two ways to keep it. PostgreSQL leaves the old row where it is and writes the new one next to it, so a table holds many versions of each row and a background process, `VACUUM`, sweeps away the dead ones. MySQL's InnoDB, HyPer and BusTub do the opposite: the table always holds the **newest** version, updated in place, and each change leaves behind a small note saying how to get back to the version before it. Those notes are **undo logs**, and the trail of them for one tuple is its **version chain**. The second design makes the common case, reading the latest data, as cheap as reading a table with no MVCC at all; the cost moves to readers who need history, who must rebuild it by applying notes backward.

## A tuple and its trail

Here is one tuple, `(a, b, c)`, that has been updated twice. It started as `(1, 2.0, false)` at timestamp 1; at timestamp 3 someone changed `a` to 4; at timestamp 5 someone changed `a` to 7 and `c` to true.

```svg
caption: A tuple (a, b, c) updated twice. The table holds the newest version; each undo log restores the columns its change touched. A reader at ts 2 applies the first log only; a reader at ts 1 applies both.
<svg viewBox="0 0 760 210" role="img" aria-label="The table tuple at ts 5 linked to two undo logs at ts 3 and ts 1">
<defs><marker id="vc-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="live" x="20" y="60" width="190" height="70" rx="3"/><text class="mid fg" x="115" y="86">table: (7, 2.0, true)</text><text class="mid dim sm" x="115" y="108">meta.ts = 5</text>
<rect class="blue" x="290" y="60" width="190" height="70" rx="3"/><text class="mid fg" x="385" y="86">log: a = 4</text><text class="mid dim sm" x="385" y="108">ts = 3, modified [a]</text>
<rect class="blue" x="560" y="60" width="180" height="70" rx="3"/><text class="mid fg" x="650" y="86">log: a = 1, c = false</text><text class="mid dim sm" x="650" y="108">ts = 1, modified [a, c]</text>
<path class="ln" d="M212 95 L288 95" marker-end="url(#vc-a)"/><path class="ln" d="M482 95 L558 95" marker-end="url(#vc-a)"/>
<text class="mid dim sm" x="250" y="82">link</text><text class="mid dim sm" x="520" y="82">prev</text>
<text class="mid fg sm" x="115" y="160">ts 5 sees (7, 2.0, true)</text><text class="mid fg sm" x="385" y="160">ts 3..4 sees (4, 2.0, true)</text><text class="mid fg sm" x="650" y="160">ts 1..2 sees (1, 2.0, false)</text>
</svg>
```

Read the figure from left to right and the story runs backward in time. The table holds `(7, 2.0, true)`, the version that became current at timestamp 5. It does not remember the earlier versions. What it has is a link, and the link points to the first undo log. That log has `a = 4`, stamped 3, and says "modified: a". Read it as: *to get from the version in front of me back to the version that was current at timestamp 3, set column a to 4.* The log after it has `a = 1, c = false`, stamped 1: *to go back further, to the version that was current at timestamp 1, set a to 1 and c to false.* Column `b` was never touched, so no log mentions it, and the value 2.0 in the table is right for every version.

Three things about this design are worth saying out loud, because the exercises will test each of them.

First, **a log holds old values, and only for the columns that changed.** A tuple with fifty columns that updates one of them leaves a log with one value in it, not fifty. That is why the design is cheap on space, and it is why a log cannot be read by itself: you need the version in front of it to fill in the columns it does not mention.

Second, **the timestamp on a log is the timestamp of the version it restores**, not of the change that created it. The log `a = 4` is stamped 3, although it was written by the transaction that committed at 5. This is the number a reader compares against, and mixing it up with the writer's timestamp is the most common mistake in this module.

Third, **the link, the head of the chain, is not part of the tuple's bytes.** The transaction manager keeps it in a separate map from tuple id to `Option<UndoLink>`. A link is a pair: which transaction's log buffer to look in, and which index in it. The logs themselves live inside the `Transaction` objects that made the changes, so when a transaction is finally garbage collected, any link that points into it stops resolving. A chain can therefore end early, and a reader must treat that as "this version is gone" and not as an error.

## Reading: which version may I see?

A transaction has a **read timestamp** `T`, the moment its snapshot was taken. It may see every change committed at or before `T` and nothing committed after. To read a tuple it asks one question: *which is the newest version whose timestamp is at most `T`?*

Use the figure and try three readers. A reader at `T = 6` looks at the table: its version is stamped 5, and 5 is at most 6, so the table's tuple is the answer, and no log is touched. This is the case the design optimises for, and the check costs one comparison.

A reader at `T = 4` finds that the table's version, 5, is too new. It follows the link to the first log, stamped 3. Is 3 at most 4? Yes: this log restores the newest version the reader may see. It stops walking. It has collected exactly one log. Applying it to the table's tuple, `a` becomes 4, and the reader gets `(4, 2.0, true)`. Notice that column `c` is still true; the log said nothing about `c`, because the change at timestamp 3 did not touch it.

A reader at `T = 2` also finds the table too new, and the first log stamped 3 is too new as well: 3 is greater than 2. So it keeps walking and collects that log, and moves to the second, stamped 1, which is at most 2. It stops there with two logs. Applying them *in order, newest first*, sets `a` to 4 and then to 1, and `c` to false: the result is `(1, 2.0, false)`. The order matters because two logs may restore the same column; the older log, applied last, must win.

A reader at `T = 0` walks off the end of the chain: every version is newer than it is. The tuple did not exist for this reader, and the right result is "no tuple", which in Rust is `None`. The same result is correct if a log in the middle of the chain has `is_deleted`, which says "before this change, the tuple did not exist": applying it turns the tuple into nothing, and a later log, one that is older, can bring it back by restoring every column.

That is the whole read algorithm, in two phases. **Collect**: walk the chain from the head, gathering logs until you reach one at or before `T`. **Apply**: starting from the table's tuple, apply the gathered logs from first to last. Keeping the phases separate has a practical reason as well as a tidy one. Collecting touches the shared chain and can fail halfway if a transaction was collected; applying is pure computation on a private copy. It also lets you decide to give up (`None`) before spending any work.

## Writing: one note per tuple per transaction

When a transaction changes a tuple for the first time, it must leave a way back. It builds a log containing the old values of the columns it is about to change, the timestamp of the version it is replacing, and the previous head of the chain as `prev_version`, and then it makes this new log the head. Chaining the new log in front of the old head, rather than overwriting it, is what makes the list of versions a list.

If the same transaction changes the same tuple again, it does **not** add a second log. Think about who reads the logs. A reader needs the version as it was *before* this transaction began, because that is the last version that was committed. The intermediate state in the middle of the transaction was never committed and is invisible to everyone else. So the transaction keeps one log and **widens** it: columns already in the log keep the original old values they have, and columns changed for the first time get their old values added. If a transaction first changes `a` and later changes `c`, its single log ends up with the old `a` and the old `c`, both from before the transaction started.

A delete is the extreme case: it must be able to bring back the whole tuple, so the log records every column. And an insert needs no log of its own, because a tuple that did not exist before leaves nothing to go back to, with one exception: if the insert reuses the slot of a tuple that was deleted, a log that says "did not exist" lets readers at older timestamps skip it.

## Partial tuples: where is column i?

A log stores its changed columns as a tuple under a **partial schema**: the table's columns picked out by `modified_fields`, in table order. Suppose a table has columns `(a, b, c, d)` and a log has `modified_fields = [true, false, true, false]`. Its partial tuple has two values, the old `a` first and the old `c` second. To find the old value for column `c`, which is column 2 of the table, you count how many modified columns come *before* it: one, `a`. So `c` is at position 1 of the partial tuple. A single left-to-right walk over the table's columns with a counter that moves only when a column is marked modified does the job in one pass; looking up each column's position separately repeats the counting and is how off-by-one errors enter.

## Where the bugs hide

The mistakes this design invites are specific. Applying logs oldest first gives the right answer for one log and the wrong answer for two. Using the timestamp of the writer instead of the version a log restores makes a reader stop one log too early or too late. Forgetting the tuple may be deleted at the table, with `base_meta.is_deleted`, means a reader sees a ghost. Treating a missing link as an error instead of "gone" makes garbage collection crash a reader. And writing a second log where one should be widened makes the chain grow with every statement. Each of these passes a test that uses a single change, and each fails the test that uses a sequence of them. That is why the tests here are sequences.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::optional<Tuple> ReconstructTuple(...)`, `std::optional<std::vector<UndoLog>> CollectUndoLogs(...)` | `Option<Tuple>`, `Option<Vec<UndoLog>>`: the same two "no such version" cases |
| `UndoLink{prev_txn_, prev_log_idx_}` read through `txn_mgr->GetUndoLog(link)` | the same pair; `get_undo_log_optional` returns `None` for a collected transaction |
| `Schema::CopySchema(schema, attrs)` for the partial schema | `Schema::copy_schema(schema, &attrs)` |

## Try it yourself

Do these on paper or in a scratch file before you read the code below. They are the check that you can use the idea, not just follow it.

1. A tuple `(x, y)` is `(9, 9)` in the table at timestamp 8. Its chain is: a log stamped 6 with `x = 5`, then a log stamped 2 with `y = 1`, then a log stamped 1 that is `is_deleted`. What does a reader at timestamp 7 see? At 3? At 1? At 0?
2. A transaction changes column `a` of a tuple, then changes column `c`, then changes `a` again. How many logs does it own for that tuple, and which old values does it hold? Why would a second log for `a` be wrong?
3. Why does the reader stop at the first log whose timestamp is *at most* `T` and not the first whose timestamp is *less than* `T`? What would a reader at exactly the timestamp of a commit miss?
4. **Kata (a week from now).** In a blank file, write `collect` and `reconstruct` for rows of `Vec<i32>` against the tests in the section below, without looking at them. Then compare with the reference implementation in your repository and note the first place you differ.
5. **Experiment.** Build a table of 10 000 tuples. Update every tuple ten times, each time by a new transaction. Time a full scan by a reader at the newest timestamp, then by a reader that began before the updates. Predict the ratio first. The performance section of 4a-04 has a hint.

## In real code

### Using it: undo logs on a small row

```rust test
#[derive(Clone, Debug, PartialEq)]
struct Log {
    ts: i64,
    deleted: bool,
    /// per column: Some(old value) if this log restores it
    cols: Vec<Option<i32>>,
}

/// Applies logs in order to `base` (None: the base is a deleted tuple).
fn reconstruct(base: Option<Vec<i32>>, logs: &[Log]) -> Option<Vec<i32>> {
    let mut row = base;
    for log in logs {
        if log.deleted {
            row = None;
            continue;
        }
        let r = row.get_or_insert_with(|| vec![0; log.cols.len()]);
        for (i, c) in log.cols.iter().enumerate() {
            if let Some(v) = c {
                r[i] = *v;
            }
        }
    }
    row
}

#[test]
fn applying_logs_walks_back_in_time() {
    // version history: ts1 (1, 10, 100) -> ts3 (4, 10, 100) -> ts5 (7, 10, 50)
    let table = vec![7, 10, 50];
    let newest_first = [
        Log { ts: 3, deleted: false, cols: vec![Some(4), None, Some(100)] },
        Log { ts: 1, deleted: false, cols: vec![Some(1), None, None] },
    ];
    assert_eq!(reconstruct(Some(table.clone()), &newest_first[..0]), Some(vec![7, 10, 50]));
    assert_eq!(reconstruct(Some(table.clone()), &newest_first[..1]), Some(vec![4, 10, 100]));
    assert_eq!(reconstruct(Some(table), &newest_first[..2]), Some(vec![1, 10, 100]));
}

#[test]
fn a_deleting_log_means_the_tuple_did_not_exist() {
    let del = Log { ts: 2, deleted: true, cols: vec![None, None] };
    assert_eq!(reconstruct(Some(vec![5, 5]), &[del]), None);
}
```

### Using it: collecting only what a reader needs

```rust test
struct Log {
    ts: i64,
}

/// The logs to apply for a reader at `read_ts`: follow the chain (newest first) until a log at or before `read_ts`.
fn collect(table_ts: i64, chain: &[Log], read_ts: i64) -> Option<Vec<&Log>> {
    if table_ts <= read_ts {
        return Some(vec![]);
    }
    let mut out = vec![];
    for log in chain {
        out.push(log);
        if log.ts <= read_ts {
            return Some(out);
        }
    }
    None
}

#[test]
fn stops_at_the_first_old_enough_log() {
    let chain = [Log { ts: 7 }, Log { ts: 3 }, Log { ts: 1 }];
    assert_eq!(collect(9, &chain, 3).unwrap().len(), 2);
    assert_eq!(collect(9, &chain, 8).unwrap().len(), 1);
    assert_eq!(collect(9, &chain, 100).unwrap().len(), 0, "the table's version is old enough for ts >= 9");
}

#[test]
fn a_reader_older_than_every_version_sees_nothing() {
    let chain = [Log { ts: 7 }, Log { ts: 3 }];
    assert!(collect(9, &chain, 2).is_none());
}
```

### In the exercises

- **4a-04:** `reconstruct_tuple` is the apply step, with the partial schema.
- **4a-05:** `collect_undo_logs` is the walk.
- **4a-06 / 4a-07:** `generate_new_undo_log` and `generate_updated_undo_log` write the logs.
- **4a-08:** the scan uses all of them for every tuple.

### Where it is used

- **MySQL InnoDB**: rows are updated in place in the clustered index; the previous contents are kept in undo logs, and a consistent read rebuilds the old version from them.
- **HyPer**: the same newest-in-place, deltas-behind layout (Neumann et al., SIGMOD 2015).
- **Oracle**: rollback / undo data is used to build read-consistent images of a block.
