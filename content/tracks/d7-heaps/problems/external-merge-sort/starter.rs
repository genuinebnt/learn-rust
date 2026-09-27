/// Merges runs that are each sorted by `key` into one sorted stream.
pub struct KMerge<I: Iterator, K, F> {
    runs: Vec<I>,
    key: F,
    // Add what you need, and drop this marker once K and I::Item are used elsewhere.
    _marker: std::marker::PhantomData<(K, I::Item)>,
}

pub fn kmerge_by_key<I, K, F>(runs: Vec<I>, key: F) -> KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    todo!()
}

impl<I, K, F> Iterator for KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        todo!()
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        todo!()
    }
}
