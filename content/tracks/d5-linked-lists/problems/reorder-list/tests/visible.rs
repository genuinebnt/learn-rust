use solution::*;

#[test]
fn even() {
    let mut l = list(&[1, 2, 3, 4]);
    check!(r#"[1,2,3,4]"#, { reorder(&mut l); values(&l) }, vec![1, 4, 2, 3]);
}

#[test]
fn odd() {
    let mut l = list(&[1, 2, 3, 4, 5]);
    check!(r#"[1,2,3,4,5]"#, { reorder(&mut l); values(&l) }, vec![1, 5, 2, 4, 3]);
}
