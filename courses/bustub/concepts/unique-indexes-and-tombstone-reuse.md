---
title: Unique indexes under MVCC: tombstones and reusing a rid
summary: Why an index entry cannot be removed when a tuple is deleted, how the index becomes the arbiter of a primary key, and how an insert of a key whose tuple is a tombstone reuses the rid instead of making a second tuple.
minutes: 8
---
A primary-key index maps each key to a rid. Under MVCC three facts make it awkward:

1. **A delete is not final.** Until every reader that can see the tuple is gone (and the delete is committed), the deleting transaction can abort, and older readers can still see the tuple. The tuple stays in the table as a *tombstone*, and so does its index entry.
2. **Visibility is per reader.** The index says "key 5 is at rid 7". Whether a reader *sees* a tuple at rid 7 depends on its snapshot. The index lookup therefore returns a rid, and the reader reconstructs the version it may see (possibly none).
3. **Two transactions may insert the same new key at once.** The index must decide which one wins.

## The rules

- **Never remove an entry on delete.** The tombstone keeps its entry; deleting is only `is_deleted = true` plus an undo log.
- **Look the key up before inserting.**
  - No entry: insert the tuple into the table (new rid, temporary timestamp), then insert the entry. If the entry insert fails, another transaction got the key first: bury the tuple you just made and fail (write-write conflict).
  - Entry, and the tuple at its rid is **live** (not deleted): duplicate key: the inserting transaction is tainted and the statement fails.
  - Entry, and the tuple is a **tombstone**: reuse the rid. Make the tombstone live again with the new values, as a normal in-place change: write-write conflict check, an undo log "the previous version was a deleted tuple" with the tombstone's timestamp, the head link moved onto it.
- **Updating a key is a delete plus an insert**, not an in-place change of the key column: the old key's entry stays and points to a tombstone, the new key gets an entry (or reuses a tombstone). Do all deletes first, then all inserts, so that `SET k = k + 1` over keys 1..4 can reuse the tombstones it has just made (key 2 is the tombstone of the old row 1's neighbour, and so on).

A lookup through the index never needs the key to be re-checked against the reconstructed tuple: a rid belongs to one key for its whole life.

```svg
caption: Key 2 across three transactions. The rid never changes; the chain says who sees what.
<svg viewBox="0 0 760 190" role="img" aria-label="One rid with a live version, a tombstone and a reinsert">
<defs><marker id="ui-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="hot" x="20" y="40" width="200" height="60" rx="3"/><text class="mid fg" x="120" y="66">table: (2, 7) ts=9</text><text class="mid dim sm" x="120" y="86">live again (txn 9 reinserted)</text>
<rect class="blue" x="290" y="40" width="200" height="60" rx="3"/><text class="mid fg" x="390" y="66">log: deleted ts=6</text><text class="mid dim sm" x="390" y="86">"before txn 9: a tombstone"</text>
<rect class="blue" x="560" y="40" width="180" height="60" rx="3"/><text class="mid fg" x="650" y="66">log: (2, 5) ts=2</text><text class="mid dim sm" x="650" y="86">"before the delete at 6"</text>
<path class="ln" d="M222 70 L288 70" marker-end="url(#ui-a)"/><path class="ln" d="M492 70 L558 70" marker-end="url(#ui-a)"/>
<text class="mid fg sm" x="120" y="130">read ts ≥ 9 sees (2, 7)</text><text class="mid fg sm" x="390" y="130">6 ≤ ts &lt; 9: no tuple</text><text class="mid fg sm" x="650" y="130">2 ≤ ts &lt; 6: (2, 5)</text>
<text class="dim sm" x="380" y="170" style="text-anchor:middle">index: 2 → this rid, the whole time</text>
</svg>
```

## C++ comparison

| C / C++ | Rust |
|---|---|
| `index->ScanKey(key, &result, txn)` and checking `result.empty()` | `index.scan_key(&key)` returns a `Vec<Rid>`; `.first()` is the rid if any |
| `if (!index->InsertEntry(key, rid, txn)) { ... }` | `if !index.insert_entry(&key, rid) { ... }` |
| tombstone reuse via `UpdateTupleInPlace` with a check lambda | `modify_tuple` (the same write path as an update) |

**Port rule:** a unique-index insert is "lookup, then decide among no entry / live / tombstone", and the decision is final only when the index insert succeeds.

## In real code

### Using it: the three cases of an insert

```rust test
use std::collections::BTreeMap;

#[derive(Debug, PartialEq)]
enum Outcome {
    New(usize),
    Reused(usize),
    Duplicate,
}

struct Table {
    rows: Vec<(bool, i32, i32)>, // (deleted, key, value)
    index: BTreeMap<i32, usize>,
}

impl Table {
    fn insert(&mut self, key: i32, value: i32) -> Outcome {
        match self.index.get(&key).copied() {
            Some(rid) if !self.rows[rid].0 => Outcome::Duplicate,
            Some(rid) => {
                self.rows[rid] = (false, key, value); // revive the tombstone
                Outcome::Reused(rid)
            }
            None => {
                self.rows.push((false, key, value));
                let rid = self.rows.len() - 1;
                self.index.insert(key, rid);
                Outcome::New(rid)
            }
        }
    }
    fn delete(&mut self, key: i32) {
        let rid = self.index[&key];
        self.rows[rid].0 = true; // the entry stays
    }
}

#[test]
fn deleting_keeps_the_entry_and_reinserting_reuses_the_rid() {
    let mut t = Table { rows: vec![], index: BTreeMap::new() };
    assert_eq!(t.insert(1, 10), Outcome::New(0));
    assert_eq!(t.insert(1, 11), Outcome::Duplicate);
    t.delete(1);
    assert_eq!(t.insert(1, 12), Outcome::Reused(0));
    assert_eq!(t.rows.len(), 1, "no second tuple was made");
}

#[test]
fn a_primary_key_update_is_all_deletes_then_all_inserts() {
    let mut t = Table { rows: vec![], index: BTreeMap::new() };
    for k in 1..=4 {
        t.insert(k, 0);
    }
    for k in 1..=4 {
        t.delete(k);
    }
    let outcomes: Vec<Outcome> = (2..=5).map(|k| t.insert(k, 0)).collect();
    assert_eq!(outcomes, vec![Outcome::Reused(1), Outcome::Reused(2), Outcome::Reused(3), Outcome::New(4)]);
    assert_eq!(t.rows.iter().filter(|r| !r.0).count(), 4);
}
```

### Using it: a lost race leaves a buried tuple

```rust test
use std::collections::HashMap;
use std::sync::Mutex;

/// `insert_entry` is the arbiter: it returns false for the second inserter of a key.
struct Index(Mutex<HashMap<i32, usize>>);

impl Index {
    fn insert_entry(&self, key: i32, rid: usize) -> bool {
        let mut m = self.0.lock().unwrap();
        if m.contains_key(&key) {
            return false;
        }
        m.insert(key, rid);
        true
    }
}

#[test]
fn the_loser_buries_its_tuple() {
    let index = Index(Mutex::new(HashMap::new()));
    let mut deleted = vec![false, false]; // two tuples, both already in the heap
    assert!(index.insert_entry(7, 0));
    if !index.insert_entry(7, 1) {
        deleted[1] = true; // bury the tuple we made, then fail the statement
    }
    assert_eq!(deleted, vec![false, true]);
    assert_eq!(index.0.lock().unwrap()[&7], 0);
}
```

### In the exercises

- **4b-06:** primary-key inserts: unique check, tombstone reuse, the race.
- **4b-07:** an update of the primary key as deletes followed by inserts.
- **4b-09:** BusTub's `txn_index_test` runs all of it.

### Where it is used

- **PostgreSQL**: a deleted row's index entry is kept until `VACUUM` removes it; a unique check looks at the heap tuple's visibility, and waits for or fails on an in-progress inserter of the same key.
- **MySQL InnoDB**: delete-marked index records stay until purge; a unique check on a delete-marked record is allowed to reuse it.
