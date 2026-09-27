use solution::*;

#[test]
fn k2() {
    check!(r#"[1,2,3,4,5], k = 2"#, values(&reverse_k_group(list(&[1, 2, 3, 4, 5]), 2)), vec![2, 1, 4, 3, 5]);
}

#[test]
fn k3() {
    check!(r#"[1,2,3,4,5], k = 3"#, values(&reverse_k_group(list(&[1, 2, 3, 4, 5]), 3)), vec![3, 2, 1, 4, 5]);
}

#[test]
fn k1() {
    check!(r#"[1,2,3], k = 1"#, values(&reverse_k_group(list(&[1, 2, 3]), 1)), vec![1, 2, 3]);
}

#[test]
fn too_long() {
    check!(r#"[1,2], k = 3"#, values(&reverse_k_group(list(&[1, 2]), 3)), vec![1, 2]);
}

#[test]
fn empty() {
    check!(r#"[], k = 2"#, reverse_k_group(None, 2), None);
}
