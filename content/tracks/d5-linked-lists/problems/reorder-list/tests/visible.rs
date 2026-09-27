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

#[test]
fn empty() {
    let mut l = None;
    check!(r#"[]"#, { reorder(&mut l); l }, None);
}

#[test]
fn short() {
    let mut l = list(&[1, 2]);
    check!(r#"[1,2]"#, { reorder(&mut l); values(&l) }, vec![1, 2]);
}

#[test]
fn three() {
    let mut l = list(&[1, 2, 3]);
    check!(r#"[1,2,3]"#, { reorder(&mut l); values(&l) }, vec![1, 3, 2]);
}
