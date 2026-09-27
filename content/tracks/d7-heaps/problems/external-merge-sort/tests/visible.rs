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

#[test]
fn three_runs() {
    check!(r#"runs = [[1, 4, 9], [2, 3], []], key = |x| *x"#, kmerge_by_key(vec![vec![1, 4, 9].into_iter(), vec![2, 3].into_iter(), vec![].into_iter()], |x: &i32| *x).collect::<Vec<_>>(), vec![1, 2, 3, 4, 9]);
}

#[test]
fn no_runs() {
    check!(r#"runs = []"#, kmerge_by_key(Vec::<std::vec::IntoIter<i32>>::new(), |x: &i32| *x).count(), 0);
}

#[test]
fn equal_keys_in_run_order() {
    check!(r#"runs = [[(1, "a0"), (2, "a1")], [(1, "b0"), (1, "b1")]], key = |r| r.0"#, kmerge_by_key(vec![vec![(1, "a0"), (2, "a1")].into_iter(), vec![(1, "b0"), (1, "b1")].into_iter()], |r: &(u32, &str)| r.0).collect::<Vec<_>>(), vec![(1, "a0"), (1, "b0"), (1, "b1"), (2, "a1")]);
}

#[test]
fn key_called_once_per_item() {
    let calls = Cell::new(0);
    let out: Vec<u32> = kmerge_by_key(vec![vec![5, 7].into_iter(), vec![1, 6, 8].into_iter()], |x: &u32| {
        calls.set(calls.get() + 1);
        *x
    })
    .collect();
    check!(r#"runs = [[5, 7], [1, 6, 8]], counting key calls"#, (out, calls.get()), (vec![1, 5, 6, 7, 8], 5));
}

#[test]
fn reads_lazily() {
    let reads: Vec<Rc<Cell<usize>>> = (0..3).map(|_| Rc::new(Cell::new(0))).collect();
    let runs: Vec<Counted<std::vec::IntoIter<u32>>> = (0..3u32).map(|r| Counted { inner: vec![r, r + 10, r + 20].into_iter(), reads: reads[r as usize].clone() }).collect();
    let taken: Vec<u32> = kmerge_by_key(runs, |x: &u32| *x).take(4).collect();
    let ahead: Vec<usize> = (0..3u32).map(|r| reads[r as usize].get() - taken.iter().filter(|&&x| x % 10 == r).count()).collect();
    check!(r#"runs = [[0, 10, 20], [1, 11, 21], [2, 12, 22]], take 4: no run read more than one item past what it returned"#, ahead.iter().all(|&a| a <= 1), true);
}

#[test]
fn exact_size_hint() {
    let mut m = kmerge_by_key(vec![vec![1, 3].into_iter(), vec![2].into_iter()], |x: &i32| *x);
    let before = m.size_hint();
    m.next();
    let after = m.size_hint();
    check!(r#"runs = [[1, 3], [2]]: size_hint before and after one next()"#, (before, after), ((3, Some(3)), (2, Some(2))));
}

#[test]
fn descending_with_reverse_key() {
    check!(r#"runs = [[9, 4, 1], [8, 2]] (each descending), key = |x| Reverse(*x)"#, kmerge_by_key(vec![vec![9, 4, 1].into_iter(), vec![8, 2].into_iter()], |x: &i32| std::cmp::Reverse(*x)).collect::<Vec<_>>(), vec![9, 8, 4, 2, 1]);
}
