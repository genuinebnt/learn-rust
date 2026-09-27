use std::cmp::Ordering;
use std::collections::BinaryHeap;

/// A run's current item with its key. Ordered so that `BinaryHeap` (a max-heap) pops the smallest
/// key first, and on equal keys the lowest run. The item itself is never compared.
struct Head<K, T> {
    key: K,
    run: usize,
    item: T,
}

impl<K: Ord, T> Ord for Head<K, T> {
    fn cmp(&self, other: &Self) -> Ordering {
        other.key.cmp(&self.key).then_with(|| other.run.cmp(&self.run))
    }
}

impl<K: Ord, T> PartialOrd for Head<K, T> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<K: Ord, T> PartialEq for Head<K, T> {
    fn eq(&self, other: &Self) -> bool {
        self.cmp(other) == Ordering::Equal
    }
}

impl<K: Ord, T> Eq for Head<K, T> {}

/// Merges runs that are each sorted by `key` into one sorted stream.
pub struct KMerge<I: Iterator, K, F> {
    runs: Vec<I>,
    key: F,
    /// At most one item per run: the next one it has to offer.
    heap: BinaryHeap<Head<K, I::Item>>,
}

pub fn kmerge_by_key<I, K, F>(mut runs: Vec<I>, mut key: F) -> KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    let mut heap = BinaryHeap::with_capacity(runs.len());
    for (run, it) in runs.iter_mut().enumerate() {
        if let Some(item) = it.next() {
            heap.push(Head { key: key(&item), run, item });
        }
    }
    KMerge { runs, key, heap }
}

impl<I, K, F> Iterator for KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        let Head { run, item, .. } = self.heap.pop()?;
        // Refill from the same run only; an exhausted run is never polled again.
        if let Some(next) = self.runs[run].next() {
            let key = (self.key)(&next);
            self.heap.push(Head { key, run, item: next });
        }
        Some(item)
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let held = self.heap.len();
        self.runs.iter().fold((held, Some(held)), |(lo, hi), run| {
            let (a, b) = run.size_hint();
            (lo.saturating_add(a), hi.zip(b).and_then(|(h, b)| h.checked_add(b)))
        })
    }
}
