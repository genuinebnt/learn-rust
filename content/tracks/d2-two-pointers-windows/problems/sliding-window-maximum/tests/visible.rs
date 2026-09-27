use solution::*;

#[test]
fn classic() {
    check!(r#"nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3"#, max_sliding_window(&[1, 3, -1, -3, 5, 3, 6, 7], 3), vec![3, 3, 5, 5, 6, 7]);
}

#[test]
fn k_one() {
    check!(r#"nums = [4, 2], k = 1"#, max_sliding_window(&[4, 2], 1), vec![4, 2]);
}
