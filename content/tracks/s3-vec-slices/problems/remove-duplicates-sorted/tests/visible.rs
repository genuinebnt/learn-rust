use solution::*;

#[test]
fn classic() {
    check!(r#"v = [0, 0, 1, 1, 1, 2]"#, { let mut v = [0, 0, 1, 1, 1, 2]; let k = dedup_sorted(&mut v); v[..k].to_vec() }, vec![0, 1, 2]);
}

#[test]
fn count() {
    check!(r#"v = [1, 1, 2]"#, dedup_sorted(&mut [1, 1, 2]), 2);
}

#[test]
fn leetcode_26_first() {
    check!(r#"v = [1, 1, 2]"#, { let mut v = [1, 1, 2]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (2, vec![1, 2]));
}

#[test]
fn leetcode_26_second() {
    check!(r#"v = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]"#, { let mut v = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (5, vec![0, 1, 2, 3, 4]));
}

#[test]
fn single() {
    check!(r#"v = [7]"#, { let mut v = [7]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (1, vec![7]));
}
