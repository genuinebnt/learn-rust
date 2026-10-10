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
    // @begin 2d-c5
    let mut v: Vec<Entry> = entries.to_vec();
    match v.binary_search_by_key(&key, |e| e.0) {
        Ok(i) => {
            v[i].1 = true;
            return Inserted::Done(v);
        }
        Err(i) => {
            if v.len() >= capacity {
                v.retain(|e| e.1);
                if v.len() >= capacity {
                    let at = v.binary_search_by_key(&key, |e| e.0).unwrap_err();
                    v.insert(at, (key, true));
                    let right = v.split_off((v.len() + 1) / 2);
                    return Inserted::Split(v, right);
                }
                let at = v.binary_search_by_key(&key, |e| e.0).unwrap_err();
                v.insert(at, (key, true));
                return Inserted::Done(v);
            }
            v.insert(i, (key, true));
        }
    }
    Inserted::Done(v)
    //~ todo!("2d-c5: revive, insert, reclaim tombstones of a full leaf, and only then split")
    // @end
}
