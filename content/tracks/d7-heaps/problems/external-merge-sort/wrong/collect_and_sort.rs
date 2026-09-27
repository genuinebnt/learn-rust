use std::marker::PhantomData;

/// Merges runs that are each sorted by `key` into one sorted stream.
pub struct KMerge<I: Iterator, K, F> {
    items: std::vec::IntoIter<(K, usize, I::Item)>,
    _key: PhantomData<F>,
}

pub fn kmerge_by_key<I, K, F>(runs: Vec<I>, mut key: F) -> KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    let mut all = Vec::new();
    for (run, it) in runs.into_iter().enumerate() {
        for item in it {
            all.push((key(&item), run, item));
        }
    }
    // Stable, so equal keys keep run order.
    all.sort_by(|a, b| a.0.cmp(&b.0).then(a.1.cmp(&b.1)));
    KMerge { items: all.into_iter(), _key: PhantomData }
}

impl<I, K, F> Iterator for KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        self.items.next().map(|(_, _, item)| item)
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.items.size_hint()
    }
}
