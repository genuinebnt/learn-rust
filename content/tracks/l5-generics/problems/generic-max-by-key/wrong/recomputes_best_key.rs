/// The item with the largest key; the first one on a tie. Calls `key` once per item.
pub fn max_by_key<T, K, F>(items: &[T], mut key: F) -> Option<&T>
where
    F: FnMut(&T) -> &K,
    K: Ord + ?Sized,
{
    let mut best: Option<&T> = None;
    for item in items {
        if best.map_or(true, |b| key(item) > key(b)) {
            best = Some(item);
        }
    }
    best
}
