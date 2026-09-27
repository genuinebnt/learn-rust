use solution::*;

#[test]
fn k1() {
    check!(r#"[1,2,3], k = 1"#, values(&reverse_k_group(list(&[1, 2, 3]), 1)), vec![1, 2, 3]);
}

#[test]
fn whole() {
    check!(r#"[1,2,3], k = 3"#, values(&reverse_k_group(list(&[1, 2, 3]), 3)), vec![3, 2, 1]);
}

#[test]
fn too_long() {
    check!(r#"[1,2], k = 3"#, values(&reverse_k_group(list(&[1, 2]), 3)), vec![1, 2]);
}

#[test]
fn long() {
    check!(r#"10⁴ nodes, k = 100"#, { let v = values(&reverse_k_group(list(&(0..10_000).collect::<Vec<i32>>()), 100)); (v[0], v[99], v[100], v.len()) }, (99, 0, 199, 10_000));
}
