use solution::*;

#[test]
fn zero_chunks() {
    check!(r#"[1, 2, 3], 0 threads"#, parallel_sum(&[1, 2, 3], 0), 6);
}

#[test]
fn more_threads_than_items() {
    check!(r#"[1, 2, 3], 10 threads"#, parallel_sum(&[1, 2, 3], 10), 6);
}

#[test]
fn big() {
    let data = vec![1u64; 1_000_000];
    check!(r#"10⁶ ones, 8 threads"#, parallel_sum(&data, 8), 1_000_000);
}
