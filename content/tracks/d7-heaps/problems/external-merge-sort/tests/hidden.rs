use solution::*;

use std::cell::Cell;
use std::rc::Rc;

/// A run that counts how many items have been read from it.
struct Counted<I> {
    inner: I,
    reads: Rc<Cell<usize>>,
}

impl<I: Iterator> Iterator for Counted<I> {
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        let x = self.inner.next();
        if x.is_some() {
            self.reads.set(self.reads.get() + 1);
        }
        x
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.inner.size_hint()
    }
}

/// No Clone, Copy, Debug, PartialEq or Ord: the merge must only move items.
struct Rec {
    key: u32,
    tag: &'static str,
}

#[test]
fn empty_runs_between() {
    check!(r#"runs = [[], [1], [], [0, 2], []]"#, kmerge_by_key(vec![vec![], vec![1], vec![], vec![0, 2], vec![]].into_iter().map(Vec::into_iter).collect(), |x: &i32| *x).collect::<Vec<_>>(), vec![0, 1, 2]);
}

#[test]
fn items_without_traits() {
    let runs = vec![vec![Rec { key: 2, tag: "x" }, Rec { key: 3, tag: "y" }].into_iter(), vec![Rec { key: 2, tag: "z" }].into_iter()];
    let out: Vec<(u32, &str)> = kmerge_by_key(runs, |r: &Rec| r.key).map(|r| (r.key, r.tag)).collect();
    check!(r#"runs of Rec { key, tag } with no derives: [[(2, "x"), (3, "y")], [(2, "z")]]"#, out, vec![(2, "x"), (2, "z"), (3, "y")]);
}

#[test]
fn owned_strings_by_length() {
    let runs: Vec<std::vec::IntoIter<String>> = vec![vec!["a".to_string(), "ccc".to_string()].into_iter(), vec!["bb".to_string(), "dd".to_string(), "eeee".to_string()].into_iter()];
    check!(r#"runs = [["a", "ccc"], ["bb", "dd", "eeee"]] as Strings, key = len"#, kmerge_by_key(runs, |s: &String| s.len()).collect::<Vec<_>>(), vec!["a", "bb", "dd", "ccc", "eeee"]);
}

#[test]
fn stops_before_the_tripwire() {
    let trip: Box<dyn Iterator<Item = u32>> = Box::new([1, 2, 10].into_iter().chain(std::iter::from_fn(|| -> Option<u32> { panic!("read further than needed") })));
    let other: Box<dyn Iterator<Item = u32>> = Box::new([3, 4, 5].into_iter());
    let m = kmerge_by_key(vec![trip, other], |x: &u32| *x);
    check!(r#"run 0 = [1, 2, 10, then panics if read]; run 1 = [3, 4, 5]; take 3"#, m.take(3).collect::<Vec<_>>(), vec![1, 2, 3]);
}

#[test]
fn unknown_length_run() {
    let mut n = 0;
    let open: Box<dyn Iterator<Item = u32>> = Box::new(std::iter::from_fn(move || { n += 1; (n <= 3).then_some(n) }));
    let closed: Box<dyn Iterator<Item = u32>> = Box::new(vec![1, 2].into_iter());
    let m = kmerge_by_key(vec![closed, open], |x: &u32| *x);
    check!(r#"runs = [[1, 2], a from_fn run with no upper bound]: size_hint().1"#, m.size_hint().1, None);
}

#[test]
fn stable_many_runs_same_key() {
    let runs: Vec<std::vec::IntoIter<(u32, usize)>> = (0..10).map(|r| vec![(7, r)].into_iter()).collect();
    check!(r#"10 runs, each [(7, run)]"#, kmerge_by_key(runs, |r: &(u32, usize)| r.0).map(|r| r.1).collect::<Vec<_>>(), (0..10).collect::<Vec<usize>>());
}

#[test]
fn one_run() {
    check!(r#"runs = [[3, 3, 5]]"#, kmerge_by_key(vec![vec![3, 3, 5].into_iter()], |x: &i32| *x).collect::<Vec<_>>(), vec![3, 3, 5]);
}

#[test]
fn extreme_keys() {
    check!(r#"runs = [[i64::MIN, i64::MAX], [0]]"#, kmerge_by_key(vec![vec![i64::MIN, i64::MAX].into_iter(), vec![0].into_iter()], |x: &i64| *x).collect::<Vec<_>>(), vec![i64::MIN, 0, i64::MAX]);
}

#[test]
fn random_vs_stable_sort() {
    let mut rng = anneal_prelude::Rng::new(720);
    for _ in 0..300 {
        let k = rng.below(6);
        let mut runs: Vec<Vec<(u32, usize, usize)>> = Vec::new();
        for r in 0..k {
            let len = rng.below(6);
            let mut keys: Vec<u32> = rng.vec(len, 0, 4);
            keys.sort_unstable();
            runs.push(keys.into_iter().enumerate().map(|(i, key)| (key, r, i)).collect());
        }
        let reads: Vec<Rc<Cell<usize>>> = (0..k).map(|_| Rc::new(Cell::new(0))).collect();
        let calls = Cell::new(0);
        let mut m = kmerge_by_key(
            runs.iter().zip(&reads).map(|(v, c)| Counted { inner: v.clone().into_iter(), reads: c.clone() }).collect(),
            |x: &(u32, usize, usize)| {
                calls.set(calls.get() + 1);
                x.0
            },
        );
        // Never more than one unreturned item per run.
        let mut returned = vec![0; k];
        let mut got = Vec::new();
        let mut lazy = true;
        while let Some(x) = m.next() {
            returned[x.1] += 1;
            lazy &= (0..k).all(|r| reads[r].get() <= returned[r] + 1);
            got.push(x);
        }
        let mut want: Vec<(u32, usize, usize)> = runs.concat();
        want.sort();
        let n = want.len();
        check!(format!("runs (key, run, index) = {runs:?}; (merged, lazy, key calls)"), (got, lazy, calls.get()), (want, true, n));
    }
}

#[test]
fn size_hint_brackets_what_is_left() {
    // Filtered runs report (0, Some(n)): the hint must still bracket the true remainder at every step.
    let runs: Vec<std::iter::Filter<std::vec::IntoIter<u32>, fn(&u32) -> bool>> =
        (0..4).map(|r| (0..10).map(|i| i * 4 + r).collect::<Vec<u32>>().into_iter().filter((|x: &u32| x % 3 != 0) as fn(&u32) -> bool)).collect();
    let total = (0..40u32).filter(|x| x % 3 != 0).count();
    let mut m = kmerge_by_key(runs, |x: &u32| *x);
    let mut left = total;
    let mut ok = true;
    loop {
        let (lo, hi) = m.size_hint();
        ok &= lo <= left && hi.is_some_and(|h| left <= h);
        if m.next().is_none() {
            break;
        }
        left -= 1;
    }
    check!("4 filtered runs over 0..40 without multiples of 3: lo <= remaining <= hi at every step", (ok, left), (true, 0));
}

#[test]
fn scale_10k_runs() {
    let mut rng = anneal_prelude::Rng::new(721);
    let runs: Vec<Vec<u32>> = (0..10_000)
        .map(|_| {
            let mut v: Vec<u32> = rng.vec(20, 0, 1_000_000_000);
            v.sort_unstable();
            v
        })
        .collect();
    let mut want = runs.concat();
    want.sort_unstable();
    let got: Vec<u32> = kmerge_by_key(runs.into_iter().map(Vec::into_iter).collect(), |x: &u32| *x).collect();
    check!("10000 runs of 20 random values", got == want, true);
}
