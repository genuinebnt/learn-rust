use solution::*;

#[test]
fn hundred() {
    let data: Vec<u64> = (1..=100).collect();
    check!(r#"1..=100, 4 threads"#, parallel_sum(&data, 4), 5050);
}

#[test]
fn empty() {
    check!(r#"[], 3 threads"#, parallel_sum(&[], 3), 0);
}

#[test]
fn zero_chunks() {
    check!(r#"[1, 2, 3], 0 threads"#, parallel_sum(&[1, 2, 3], 0), 6);
}

#[test]
fn uneven_split() {
    check!(r#"[1, 2, 3, 4, 5, 6, 7], 3 threads"#, parallel_sum(&[1, 2, 3, 4, 5, 6, 7], 3), 28);
}

#[test]
fn data_still_usable() {
    let data = vec![1u64, 2, 3, 4];
    check!(r#"sum twice, then read data"#, (parallel_sum(&data, 2), parallel_sum(&data, 3), data.len()), (10, 10, 4));
}
