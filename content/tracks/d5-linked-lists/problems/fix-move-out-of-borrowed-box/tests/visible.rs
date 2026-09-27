use solution::*;

#[test]
fn pops() {
    let mut l = list(&[1, 2, 3]);
    check!(r#"[1,2,3]; pop twice"#, (pop_front(&mut l), pop_front(&mut l), values(&l)), (Some(1), Some(2), vec![3]));
}

#[test]
fn empty() {
    check!(r#"[]; pop"#, pop_front(&mut None), None);
}
