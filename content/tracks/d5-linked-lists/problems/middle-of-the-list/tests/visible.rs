use solution::*;

#[test]
fn odd() {
    let l = list(&[1, 2, 3, 4, 5]);
    check!(r#"[1,2,3,4,5]"#, middle(&l).map(|n| n.val), Some(3));
}

#[test]
fn even() {
    let l = list(&[1, 2, 3, 4, 5, 6]);
    check!(r#"[1,2,3,4,5,6]"#, middle(&l).map(|n| n.val), Some(4));
}
