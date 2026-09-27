use solution::*;

#[test]
fn push_then_pop() {
    let mut l = list(&[1]);
    check!(r#"push 5 onto [1]; pop"#, { push_front(&mut l, 5); (pop_front(&mut l), values(&l)) }, (Some(5), vec![1]));
}

#[test]
fn drain() {
    let mut l = list(&[4, 5]);
    check!(r#"[4,5]; pop three times"#, (pop_front(&mut l), pop_front(&mut l), pop_front(&mut l), l), (Some(4), Some(5), None, None));
}
