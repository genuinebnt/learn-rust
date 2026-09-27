/// The item with the largest key; the first one on a tie. Calls `key` once per item.
pub fn max_by_key<T, K, F>(items: &[T], mut key: F) -> Option<&T>
where
    F: FnMut(&T) -> K,
{
    todo!()
}
