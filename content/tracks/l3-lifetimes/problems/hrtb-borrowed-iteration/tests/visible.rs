use solution::*;

#[test]
fn vec_mean() {
    check!(r#"Vec [1, 2, 3]"#, Stats::new(vec![1u32, 2, 3]).mean(), Some(2.0));
}

#[test]
fn deque_spread() {
    check!(r#"VecDeque [5, 1]"#, Stats::new(std::collections::VecDeque::from([5u32, 1])).spread(), Some(4));
}
