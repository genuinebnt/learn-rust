use std::cmp::{Ordering, Reverse};
use std::collections::BinaryHeap;
use std::hash::{Hash, Hasher};

/// A sensor reading. It must work as a key in heaps, B-tree sets and hash sets.
#[derive(Debug, Clone, Copy)]
pub struct Reading(pub f64);

impl Ord for Reading {
    fn cmp(&self, other: &Self) -> Ordering {
        self.0.total_cmp(&other.0)
    }
}

impl PartialOrd for Reading {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Reading {
    fn eq(&self, other: &Self) -> bool {
        self.cmp(other) == Ordering::Equal
    }
}

impl Eq for Reading {}

impl Hash for Reading {
    // total_cmp says Equal exactly when the bits match, so hashing the bits agrees with Eq.
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.0.to_bits().hash(state);
    }
}

/// The `k` highest readings, highest first. NaN readings are sensor faults and are skipped.
/// The heap never holds more than `k + 1` readings.
pub fn top_k(readings: &[f64], k: usize) -> Vec<Reading> {
    let mut heap: BinaryHeap<Reverse<Reading>> = BinaryHeap::with_capacity(k + 1);
    for &r in readings {
        if r.is_nan() {
            continue;
        }
        heap.push(Reverse(Reading(r)));
        if heap.len() > k {
            heap.pop();
        }
    }
    // Ascending by Reverse<Reading> is descending by Reading.
    heap.into_sorted_vec().into_iter().map(|Reverse(r)| r).collect()
}
