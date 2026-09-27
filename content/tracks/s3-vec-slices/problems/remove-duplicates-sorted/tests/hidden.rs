use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, dedup_sorted(&mut []), 0);
}

#[test]
fn all_distinct() {
    check!(r#"v = [-3, 0, 7]"#, { let mut v = [-3, 0, 7]; let k = dedup_sorted(&mut v); v[..k].to_vec() }, vec![-3, 0, 7]);
}
