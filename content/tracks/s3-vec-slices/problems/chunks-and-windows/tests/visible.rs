use solution::*;

#[test]
fn chunks() {
    check!(r#"v = [1, 2, 3, 4, 5], size = 2"#, chunk_sums(&[1, 2, 3, 4, 5], 2), vec![3, 7, 5]);
}

#[test]
fn windows() {
    check!(r#"v = [1, -2, 3, 4, -1], k = 2"#, max_window_sum(&[1, -2, 3, 4, -1], 2), Some(7));
}
