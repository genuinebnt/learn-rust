use solution::*;

#[test]
fn classic() {
    check!(r#"nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3"#, max_sliding_window(&[1, 3, -1, -3, 5, 3, 6, 7], 3), vec![3, 3, 5, 5, 6, 7]);
}

#[test]
fn k_one() {
    check!(r#"nums = [4, 2], k = 1"#, max_sliding_window(&[4, 2], 1), vec![4, 2]);
}

#[test]
fn single() {
    check!(r#"nums = [1], k = 1"#, max_sliding_window(&[1], 1), vec![1]);
}

#[test]
fn whole() {
    check!(r#"nums = [9, 10, 9, -7], k = 4"#, max_sliding_window(&[9, 10, 9, -7], 4), vec![10]);
}

#[test]
fn max_leaves_window() {
    check!(r#"nums = [9, 1, 1, 1], k = 2"#, max_sliding_window(&[9, 1, 1, 1], 2), vec![9, 1, 1]);
}
