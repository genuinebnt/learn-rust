use solution::*;

#[test]
fn vec_mean() {
    check!(r#"Vec [1, 2, 3]"#, Stats::new(vec![1u32, 2, 3]).mean(), Some(2.0));
}

#[test]
fn deque_spread() {
    check!(r#"VecDeque [5, 1]"#, Stats::new(std::collections::VecDeque::from([5u32, 1])).spread(), Some(4));
}

#[test]
fn empty() {
    let s = Stats::new(Vec::<u32>::new());
    check!(r#"empty Vec"#, (s.mean(), s.spread(), s.count_above(0)), (None, None, 0));
}

#[test]
fn strictly_above() {
    check!(r#"[1, 5, 9], above 5"#, Stats::new(vec![1u32, 5, 9]).count_above(5), 1);
}

#[test]
fn fractional_mean() {
    check!(r#"BTreeSet {1, 10}"#, Stats::new(std::collections::BTreeSet::from([1u32, 10])).mean(), Some(5.5));
}
