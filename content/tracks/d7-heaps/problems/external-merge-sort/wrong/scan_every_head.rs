/// Merges runs that are each sorted by `key` into one sorted stream.
pub struct KMerge<I: Iterator, K, F> {
    runs: Vec<I>,
    key: F,
    heads: Vec<Option<(K, I::Item)>>,
}

pub fn kmerge_by_key<I, K, F>(mut runs: Vec<I>, mut key: F) -> KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    let heads = runs.iter_mut().map(|it| it.next().map(|x| (key(&x), x))).collect();
    KMerge { runs, key, heads }
}

impl<I, K, F> Iterator for KMerge<I, K, F>
where
    I: Iterator,
    K: Ord,
    F: FnMut(&I::Item) -> K,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        let mut best: Option<usize> = None;
        for r in 0..self.heads.len() {
            if let Some((k, _)) = &self.heads[r] {
                if best.is_none_or(|b| k < &self.heads[b].as_ref().unwrap().0) {
                    best = Some(r);
                }
            }
        }
        let r = best?;
        let refill = self.runs[r].next().map(|x| ((self.key)(&x), x));
        let (_, item) = std::mem::replace(&mut self.heads[r], refill)?;
        Some(item)
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let held = self.heads.iter().filter(|h| h.is_some()).count();
        self.runs.iter().fold((held, Some(held)), |(lo, hi), run| {
            let (a, b) = run.size_hint();
            (lo.saturating_add(a), hi.zip(b).and_then(|(h, b)| h.checked_add(b)))
        })
    }
}
