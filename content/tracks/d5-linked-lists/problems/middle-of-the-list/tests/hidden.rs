use solution::*;

#[test]
fn single() {
    let l = list(&[9]);
    check!(r#"[9]"#, middle(&l).map(|n| n.val), Some(9));
}

#[test]
fn empty() {
    check!(r#"[]"#, middle(&None).is_none(), true);
}

#[test]
fn two() {
    let l = list(&[1, 2]);
    check!(r#"[1,2]"#, middle(&l).map(|n| n.val), Some(2));
}
