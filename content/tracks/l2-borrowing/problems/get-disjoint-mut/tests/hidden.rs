use solution::*;

#[test]
fn out_of_bounds() {
    check!(r#"0 → 7"#, { let mut b = [10, 0]; transfer(&mut b, 0, 7, 1) }, Err("no such account"));
}

#[test]
fn insufficient() {
    check!(r#"[1, 0], 0 → 1, 5"#, { let mut b = [1, 0]; (transfer(&mut b, 0, 1, 5), b) }, (Err("insufficient funds"), [1, 0]));
}
