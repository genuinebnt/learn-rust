use solution::*;

#[test]
fn mixed() {
    check!(r#"[84,-37,32,40,95], k = 167"#, shortest_subarray(&[84, -37, 32, 40, 95], 167), Some(3));
}

#[test]
fn negative_prefix() {
    check!(r#"[-28,81,-20,28,-29], k = 89"#, shortest_subarray(&[-28, 81, -20, 28, -29], 89), Some(3));
}

#[test]
fn big() {
    let mut v = vec![1i64; 100_000];
    v[99_998] = 1_500_000_000;
    v[99_999] = 1_500_000_000;
    check!(r#"10⁵ values, k needs the last two"#, shortest_subarray(&v, 3_000_000_000), Some(2));
}
