use solution::*;

#[test]
fn window_too_big() {
    check!(r#"v = [1, 2], k = 3"#, max_window_sum(&[1, 2], 3), None);
}

#[test]
fn chunks_empty() {
    check!(r#"v = [], size = 3"#, chunk_sums(&[], 3), Vec::<i32>::new());
}
