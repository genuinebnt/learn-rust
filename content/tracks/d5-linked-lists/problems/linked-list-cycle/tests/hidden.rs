use solution::*;

#[test]
fn self_loop() {
    check!(r#"0→0"#, cycle_start(&[Some(0)], Some(0)), Some(0));
}

#[test]
fn empty() {
    check!(r#"no head"#, cycle_start(&[], None), None);
}

#[test]
fn big_loop() {
    let mut next: Vec<Option<usize>> = (1..=100_000).map(Some).collect();
    next[99_999] = Some(40_000);
    check!(r#"10⁵ nodes, last points to 40_000"#, cycle_start(&next, Some(0)), Some(40_000));
}
