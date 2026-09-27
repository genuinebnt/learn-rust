use solution::*;

#[test]
fn all_same() {
    check!(r#"[7,7,7,7]"#, values(&dedup_sorted(list(&[7, 7, 7, 7]))), vec![7]);
}

#[test]
fn empty() {
    check!(r#"[]"#, dedup_sorted(None), None);
}

#[test]
fn long() {
    let v: Vec<i32> = (0..10_000).map(|i| i / 2).collect();
    check!(r#"10⁴ values, each twice"#, values(&dedup_sorted(list(&v))).len(), 5_000);
}
