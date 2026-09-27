use solution::*;

#[test]
fn leetcode_26() {
    check!(r#"v = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4], k = 1"#, { let mut v = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]; let n = dedup_keep(&mut v, 1); (n, v[..n].to_vec()) }, (5, vec![0, 1, 2, 3, 4]));
}

#[test]
fn leetcode_80_first() {
    check!(r#"v = [1, 1, 1, 2, 2, 3], k = 2"#, { let mut v = [1, 1, 1, 2, 2, 3]; let n = dedup_keep(&mut v, 2); (n, v[..n].to_vec()) }, (5, vec![1, 1, 2, 2, 3]));
}

#[test]
fn leetcode_80_second() {
    check!(r#"v = [0, 0, 1, 1, 1, 1, 2, 3, 3], k = 2"#, { let mut v = [0, 0, 1, 1, 1, 1, 2, 3, 3]; let n = dedup_keep(&mut v, 2); (n, v[..n].to_vec()) }, (7, vec![0, 0, 1, 1, 2, 3, 3]));
}

#[test]
fn empty() {
    check!(r#"v = [], k = 2"#, { let mut v: [i32; 0] = []; let n = dedup_keep(&mut v, 2); (n, v[..n].to_vec()) }, (0, vec![]));
}

#[test]
fn vec_truncated() {
    check!(r#"v = [1, 1, 1, 1], k = 3"#, { let mut v = vec![1, 1, 1, 1]; dedup_keep_vec(&mut v, 3); v }, vec![1, 1, 1]);
}
