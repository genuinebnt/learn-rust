use solution::*;

#[test]
fn every_first() {
    check!(r#"(0..5).every_nth(1)"#, (0..5).every_nth(1).collect::<Vec<_>>(), vec![0, 1, 2, 3, 4]);
}

#[test]
fn n_past_the_end() {
    check!(r#"(0..3).every_nth(10)"#, (0..3).every_nth(10).collect::<Vec<_>>(), vec![0]);
}

#[test]
fn empty() {
    check!(r#"(0..0).every_nth(2)"#, (0..0).every_nth(2).count(), 0);
}

#[test]
fn zero_panics() {
    check!(r#"(0..5).every_nth(0)"#, std::panic::catch_unwind(|| (0..5).every_nth(0).count()).is_err(), true);
}

#[test]
fn size_hint_after_next() {
    let mut it = (0..10).every_nth(3);
    it.next();
    check!(r#"(0..10).every_nth(3) after one next"#, (it.size_hint(), it.count()), ((3, Some(3)), 3));
}

#[test]
fn size_hint_exact_multiple() {
    check!(r#"(0..9).every_nth(3)"#, (0..9).every_nth(3).size_hint(), (3, Some(3)));
}

#[test]
fn size_hint_unbounded() {
    check!(r#"(0u64..).every_nth(2), upper bound"#, (0u64..).every_nth(2).size_hint().1, None);
}

#[test]
fn dedup_all_same() {
    check!(r#"[7, 7, 7]"#, [7, 7, 7].into_iter().dedup_adjacent().collect::<Vec<_>>(), vec![7]);
}

#[test]
fn dedup_alternating() {
    check!(r#"[1, 2, 1, 2]"#, [1, 2, 1, 2].into_iter().dedup_adjacent().collect::<Vec<_>>(), vec![1, 2, 1, 2]);
}

#[test]
fn dedup_lazy_on_infinite() {
    check!(r#"(0u64..).map(|x| x / 3).dedup_adjacent().take(4)"#, (0u64..).map(|x| x / 3).dedup_adjacent().take(4).collect::<Vec<_>>(), vec![0, 1, 2, 3]);
}

#[test]
fn every_nth_pulls_only_what_it_needs() {
    let pulled = std::cell::Cell::new(0);
    let got: Vec<i32> = (0..100).inspect(|_| pulled.set(pulled.get() + 1)).every_nth(3).take(2).collect();
    check!(r#"(0..100) with a pull counter, every_nth(3).take(2)"#, (got, pulled.get()), (vec![0, 3], 4));
}

#[test]
fn counts_empty() {
    check!(r#"std::iter::empty::<u8>().counts()"#, std::iter::empty::<u8>().counts().len(), 0);
}

#[test]
fn works_on_a_custom_iterator() {
    struct Fib(u64, u64);
    impl Iterator for Fib {
        type Item = u64;
        fn next(&mut self) -> Option<u64> {
            let x = self.0;
            *self = Fib(self.1, self.0 + self.1);
            Some(x)
        }
    }
    check!("Fib.every_nth(2).take(5)", Fib(0, 1).every_nth(2).take(5).collect::<Vec<_>>(), vec![0, 1, 3, 8, 21]);
    check!("Fib.dedup_adjacent().take(4)", Fib(0, 1).dedup_adjacent().take(4).collect::<Vec<_>>(), vec![0, 1, 2, 3]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4421);
    for _ in 0..300 {
        let len = rng.below(12);
        let v: Vec<u8> = rng.vec(len, 0, 2);
        let n = rng.below(4) + 1;
        check!(format!("{v:?}.every_nth({n})"), v.iter().copied().every_nth(n).collect::<Vec<_>>(), v.iter().copied().step_by(n).collect::<Vec<_>>());
        let skip = rng.below(len + 1);
        let mut it = v.iter().every_nth(n);
        for _ in 0..skip.min(2) {
            it.next();
        }
        let hint = it.size_hint();
        let rest = it.count();
        check!(format!("{v:?}.every_nth({n}) size_hint after {} next", skip.min(2)), hint, (rest, Some(rest)));
        let mut d = v.clone();
        d.dedup();
        check!(format!("{v:?}.dedup_adjacent()"), v.iter().copied().dedup_adjacent().collect::<Vec<_>>(), d);
        let mut c: Vec<(u8, usize)> = v.iter().copied().counts().into_iter().collect();
        c.sort();
        let want: Vec<(u8, usize)> = (0..=2).map(|k| (k, v.iter().filter(|&&x| x == k).count())).filter(|&(_, n)| n > 0).collect();
        check!(format!("{v:?}.counts()"), c, want);
    }
}
