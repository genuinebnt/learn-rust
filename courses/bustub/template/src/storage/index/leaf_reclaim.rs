//! Reclaim tombstones before splitting a leaf.

/// `(key, live)`; `live == false` is a tombstone.
pub type Entry = (i32, bool);

#[derive(Debug, PartialEq, Eq)]
pub enum Inserted {
    Done(Vec<Entry>),
    Split(Vec<Entry>, Vec<Entry>),
}

/// Inserts `key` (live) into the sorted leaf `entries` of at most `capacity` entries.
pub fn insert_into_leaf(entries: &[Entry], capacity: usize, key: i32) -> Inserted {
    todo!("2d-c5: revive, insert, reclaim tombstones of a full leaf, and only then split")
}
