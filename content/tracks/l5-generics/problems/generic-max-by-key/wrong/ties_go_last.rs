/// The item with the largest key; the first one on a tie. Calls `key` once per item.
pub fn max_by_key<T, K, F>(items: &[T], mut key: F) -> Option<&T>
where
    F: FnMut(&T) -> &K,
    K: Ord + ?Sized,
{
    let mut best = None;
    for item in items {
        let k = key(item);
        if best.as_ref().map_or(true, |(_, bk)| k >= *bk) {
            best = Some((item, k));
        }
    }
    best.map(|(item, _)| item)
}
