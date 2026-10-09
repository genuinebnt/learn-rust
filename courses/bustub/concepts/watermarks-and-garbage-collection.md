---
title: The watermark: which old versions can be thrown away
summary: Why the smallest read timestamp among running transactions decides what is garbage, how to track it in logarithmic time with an ordered map of counts, and which versions of a chain can be dropped.
minutes: 7
---
Versions pile up: every update leaves an undo log, every transaction keeps its logs. They can be thrown away once **no transaction can ever need them**. Who can need a version? A transaction that is running now (it reads at its own read timestamp), or one that begins later (it reads at a read timestamp no smaller than the last commit). So the smallest read timestamp that can still occur is

> **watermark = the smallest read timestamp of the running transactions, or the last commit timestamp if none runs.**

```svg
caption: A version chain of one tuple, newest on the left, with the watermark at 4. The newest version at or below the watermark (ts 3) is still needed by the reader at 4; everything older (ts 1) is garbage.
<svg viewBox="0 0 760 170" role="img" aria-label="A version chain with the watermark between versions">
<rect class="live" x="20" y="40" width="130" height="50" rx="3"/><text class="mid fg" x="85" y="70">table  ts 9</text>
<rect class="live" x="190" y="40" width="130" height="50" rx="3"/><text class="mid fg" x="255" y="70">log  ts 6</text>
<rect class="live" x="360" y="40" width="130" height="50" rx="3"/><text class="mid fg" x="425" y="70">log  ts 3</text>
<rect class="free" x="530" y="40" width="130" height="50" rx="3"/><text class="mid dim" x="595" y="70">log  ts 1</text>
<line class="ln" x1="500" y1="20" x2="500" y2="120"/><text class="mid blue sm" x="500" y="14">watermark 4</text>
<text class="mid dim sm" x="595" y="112">garbage</text><text class="mid fg sm" x="300" y="140">kept: the reader at 4 may need ts 3, readers at 6 need ts 6, ...</text>
</svg>
```

## What is garbage in one chain

Walk the chain from the newest version. The first version whose timestamp is **at or below the watermark** is the oldest one anybody can still be looking for (the reader at the watermark reads exactly it). Every version *older than that* is unreachable. If the table's own version is at or below the watermark, the whole chain is garbage and the tuple needs no history at all.

A deleted tuple whose delete is at or below the watermark can go too: every reader sees the delete (or a later insert over its slot).

## Tracking the watermark

A transaction registers its read timestamp when it begins and removes it when it commits or aborts. Many transactions can share a read timestamp, so the set is really a **multiset**; the watermark is its minimum. An ordered map from timestamp to count does it in logarithmic time per operation:

- add: `*map.entry(ts).or_insert(0) += 1`
- remove: decrement; when the count reaches 0, remove the key
- minimum: `map.keys().next()`

A plain `Vec` with a scan for the minimum is `O(n)` per query; with a million transactions that is the difference between a test taking milliseconds and taking minutes.

## When to collect

Collection is *stop-the-world* in BusTub (`garbage_collection` is only called when no transaction is touching the table) but real systems collect in the background, usually per page, and only when the watermark has moved.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::map<timestamp_t, int> current_reads_` and `current_reads_.begin()->first` | `BTreeMap<i64, usize>` and `map.keys().next()` (or `first_key_value()`) |
| `current_reads_[ts]++` (inserts a zero first) | `*map.entry(ts).or_insert(0) += 1` |

**Port rule:** `std::map` with a counter is `BTreeMap` with `entry`; `std::unordered_map` is the wrong tool whenever you need the minimum.

## In real code

### Using it: a counting ordered map

```rust test
use std::collections::BTreeMap;

struct Watermark {
    commit_ts: i64,
    reads: BTreeMap<i64, usize>,
}

impl Watermark {
    fn new() -> Watermark {
        Watermark { commit_ts: 0, reads: BTreeMap::new() }
    }
    fn add(&mut self, ts: i64) {
        *self.reads.entry(ts).or_insert(0) += 1;
    }
    fn remove(&mut self, ts: i64) {
        if let Some(n) = self.reads.get_mut(&ts) {
            *n -= 1;
            if *n == 0 {
                self.reads.remove(&ts);
            }
        }
    }
    fn watermark(&self) -> i64 {
        self.reads.keys().next().copied().unwrap_or(self.commit_ts)
    }
}

#[test]
fn the_minimum_follows_the_oldest_reader() {
    let mut w = Watermark::new();
    for ts in [3, 1, 2] {
        w.add(ts);
    }
    assert_eq!(w.watermark(), 1);
    w.remove(1);
    assert_eq!(w.watermark(), 2);
    w.remove(3);
    assert_eq!(w.watermark(), 2);
}

#[test]
fn equal_timestamps_are_counted() {
    let mut w = Watermark::new();
    w.add(5);
    w.add(5);
    w.remove(5);
    assert_eq!(w.watermark(), 5);
    w.commit_ts = 8;
    w.remove(5);
    assert_eq!(w.watermark(), 8);
}
```

### Using it: which versions of a chain survive

```rust test
/// `chain_ts` is the timestamp of each version, newest first (the table's version first). Returns how many versions to keep.
fn keep(chain_ts: &[i64], watermark: i64) -> usize {
    match chain_ts.iter().position(|&ts| ts <= watermark) {
        Some(i) => i + 1, // keep up to and including the first version at or below the watermark
        None => chain_ts.len(), // every version is newer than the watermark: all may be needed
    }
}

#[test]
fn versions_older_than_the_one_at_the_watermark_go() {
    assert_eq!(keep(&[9, 6, 3, 1], 4), 3);
    assert_eq!(keep(&[9, 6, 3, 1], 6), 2);
}

#[test]
fn a_table_version_below_the_watermark_needs_no_history() {
    assert_eq!(keep(&[3, 2, 1], 5), 1);
    assert_eq!(keep(&[9, 8], 1), 2, "nobody reads this low: nothing is old enough to be dropped");
}
```

### In the exercises

- **4a-01:** the `Watermark` itself, with the counting ordered map above.
- **4a-02 / 4a-03:** `begin` registers a read timestamp, `commit` and `abort` remove it.
- **Module 4b:** `garbage_collection` applies the second rule to every tuple, and drops transactions whose logs are all gone.

### Where it is used

- **PostgreSQL**: `VACUUM` removes row versions that no snapshot can see, computed from the oldest `xmin` among running transactions (the "xmin horizon").
- **MySQL InnoDB**: the *purge* thread removes undo records older than the oldest read view.
- **HyPer / DuckDB-style engines**: undo buffers of finished transactions are freed once no active transaction started before they committed.
