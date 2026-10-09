---
title: Version chains and undo logs: rebuilding an older tuple
summary: How the table keeps only the newest version, how each change leaves a small undo log behind, and how a reader walks the chain and applies logs to get the version it may see.
minutes: 9
---
In BusTub's MVCC design the table heap always holds the **newest** version of a tuple, updated in place. Everything older is a chain of **undo logs**, each saying how to turn a version into the one before it.

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

## The pieces

- **The head link.** For each tuple (by rid) the transaction manager keeps an `Option<UndoLink>`: which transaction's log, and which index in it. It is *not* part of the tuple's bytes.
- **An undo log** has the timestamp of the version it restores, a flag `is_deleted` ("before this change the tuple did not exist"), `modified_fields: Vec<bool>` (which columns it restores), a *partial tuple* holding exactly those columns, and `prev_version`, the link to the next older log.
- **Ownership.** Each log lives in the `Transaction` that made the change; a link is `(txn id, log index)`. When the transaction is garbage collected, links to it stop resolving.

## Reading: collect, then apply

To read a tuple as of timestamp `T`:

1. Look at the table's version. If its timestamp is `<= T` (or it is the reader's own uncommitted write), that is the answer. No logs.
2. Otherwise follow the chain from the head link, collecting logs **until one whose `ts <= T`**: that log restores the newest version the reader may see. If the chain ends first, or a log has been collected, the tuple did not exist for this reader.
3. Apply the collected logs to the table's tuple **in order, newest first**: a log that `is_deleted` makes the result "no tuple"; any other log overwrites the columns it lists.

## Writing: one log per tuple per transaction

The first time a transaction changes a tuple it adds a log: the columns that changed (with their *old* values), the old version's timestamp, and the previous head as `prev_version`. If it changes the same tuple again, it does **not** add a log: it widens the one it has, keeping the original values of columns already logged and adding the old values of columns changed now. A delete logs every column. A tuple the transaction inserts needs a log that says "did not exist" only when it reuses a rid that held a deleted tuple.

## Partial tuples

A log's tuple holds only the modified columns, laid out under a **partial schema** (the table's columns picked by `modified_fields`, in table order). To read column `i` of the table out of a log, count how many modified columns come before `i`: that is its position in the partial tuple.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::optional<Tuple> ReconstructTuple(...)`, `std::optional<std::vector<UndoLog>> CollectUndoLogs(...)` | `Option<Tuple>`, `Option<Vec<UndoLog>>`: the same two "no such version" cases |
| `UndoLink{prev_txn_, prev_log_idx_}` read through `txn_mgr->GetUndoLog(link)` | the same pair; `get_undo_log_optional` returns `None` for a collected transaction |
| `Schema::CopySchema(schema, attrs)` for the partial schema | `Schema::copy_schema(schema, &attrs)` |

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
