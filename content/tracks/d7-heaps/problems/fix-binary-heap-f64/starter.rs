use std::cmp::Reverse;
use std::collections::BinaryHeap;

/// A sensor reading. It must work as a key in heaps, B-tree sets and hash sets.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Hash)]
pub struct Reading(pub f64);

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
