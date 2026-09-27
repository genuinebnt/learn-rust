use solution::*;

#[test]
fn classic() {
    check!(r#"v = [0, 0, 1, 1, 1, 2]"#, { let mut v = [0, 0, 1, 1, 1, 2]; let k = dedup_sorted(&mut v); v[..k].to_vec() }, vec![0, 1, 2]);
}

#[test]
fn count() {
    check!(r#"v = [1, 1, 2]"#, dedup_sorted(&mut [1, 1, 2]), 2);
}
