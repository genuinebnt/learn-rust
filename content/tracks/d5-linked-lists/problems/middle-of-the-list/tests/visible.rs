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

#[test]
fn single() {
    let l = list(&[9]);
    check!(r#"[9]"#, middle(&l).map(|n| n.val), Some(9));
}

#[test]
fn two() {
    let l = list(&[1, 2]);
    check!(r#"[1,2]"#, middle(&l).map(|n| n.val), Some(2));
}

#[test]
fn empty() {
    check!(r#"[]"#, middle(&None).is_none(), true);
}
