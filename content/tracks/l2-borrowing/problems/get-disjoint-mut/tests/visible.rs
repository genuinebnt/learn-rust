use solution::*;

#[test]
fn moves() {
    check!(r#"[10, 0], 0 → 1, 4"#, { let mut b = [10, 0]; (transfer(&mut b, 0, 1, 4), b) }, (Ok(()), [6, 4]));
}

#[test]
fn same() {
    check!(r#"0 → 0"#, { let mut b = [10]; transfer(&mut b, 0, 0, 1) }, Err("same account"));
}
