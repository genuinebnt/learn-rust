use solution::*;

#[test]
fn short() {
    let mut l = list(&[1, 2]);
    check!(r#"[1,2]"#, { reorder(&mut l); values(&l) }, vec![1, 2]);
}

#[test]
fn empty() {
    let mut l = None;
    check!(r#"[]"#, { reorder(&mut l); l }, None);
}

#[test]
fn long() {
    let mut l = list(&(0..10_000).collect::<Vec<_>>());
    check!(r#"10⁴ nodes: first and last swap in"#, { reorder(&mut l); values(&l)[..4].to_vec() }, vec![0, 9_999, 1, 9_998]);
}
