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
