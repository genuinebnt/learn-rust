use solution::*;

#[test]
fn moves() {
    check!(r#"[10, 0], 0 → 1, 4"#, { let mut b = [10, 0]; (transfer(&mut b, 0, 1, 4), b) }, (Ok(()), [6, 4]));
}

#[test]
fn same() {
    check!(r#"0 → 0"#, { let mut b = [10]; transfer(&mut b, 0, 0, 1) }, Err("same account"));
}

#[test]
fn exact_balance() {
    check!(r#"[5, 0], 0 → 1, 5"#, { let mut b = [5, 0]; (transfer(&mut b, 0, 1, 5), b) }, (Ok(()), [0, 5]));
}

#[test]
fn reverse() {
    check!(r#"[0, 10], 1 → 0, 3"#, { let mut b = [0, 10]; (transfer(&mut b, 1, 0, 3), b) }, (Ok(()), [3, 7]));
}

#[test]
fn same_checked_before_funds() {
    check!(r#"[0], 0 → 0, 5"#, { let mut b = [0]; transfer(&mut b, 0, 0, 5) }, Err("same account"));
}
