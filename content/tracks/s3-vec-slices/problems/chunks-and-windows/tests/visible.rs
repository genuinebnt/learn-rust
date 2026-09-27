use solution::*;

#[test]
fn chunks() {
    check!(r#"v = [1, 2, 3, 4, 5], size = 2"#, chunk_sums(&[1, 2, 3, 4, 5], 2), vec![3, 7, 5]);
}

#[test]
fn windows() {
    check!(r#"v = [1, -2, 3, 4, -1], k = 2"#, max_window_sum(&[1, -2, 3, 4, -1], 2), Some(7));
}

#[test]
fn leetcode_643() {
    check!(r#"v = [1, 12, -5, -6, 50, 3], k = 4"#, max_window_sum(&[1, 12, -5, -6, 50, 3], 4), Some(51));
}

#[test]
fn window_is_whole_slice() {
    check!(r#"v = [5], k = 1"#, max_window_sum(&[5], 1), Some(5));
}

#[test]
fn chunk_bigger_than_v() {
    check!(r#"v = [1, 2], size = 5"#, chunk_sums(&[1, 2], 5), vec![3]);
}
