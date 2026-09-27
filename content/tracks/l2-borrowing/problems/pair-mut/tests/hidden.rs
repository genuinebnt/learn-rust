use solution::*;

#[test]
fn order_kept() {
    check!(r#"i = 2, j = 0"#, { let mut v = [10, 20, 30]; let (a, b) = pair_mut(&mut v, 2, 0).unwrap(); (*a, *b) }, (30, 10));
}

#[test]
fn out_of_bounds() {
    check!(r#"j = 5"#, pair_mut(&mut [1, 2], 0, 5).is_none(), true);
}
