use solution::*;

#[test]
fn whole() {
    check!(r#"nums = [9, 10, 9, -7], k = 4"#, max_sliding_window(&[9, 10, 9, -7], 4), vec![10]);
}

#[test]
fn descending() {
    check!(r#"nums = [5, 4, 3, 2, 1], k = 2"#, max_sliding_window(&[5, 4, 3, 2, 1], 2), vec![5, 4, 3, 2]);
}

#[test]
fn large() {
    check!(r#"nums = 0..100000, k = 1000"#, max_sliding_window(&(0..100_000).collect::<Vec<_>>(), 1000).len(), 99001);
}
