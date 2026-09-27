use solution::*;

#[test]
fn transfer_example() {
    check!(r#"[10, 0], 0 -> 1, 4"#, { let mut b = [10, 0]; (transfer(&mut b, 0, 1, 4), b) }, (Ok(()), [6, 4]));
}

#[test]
fn settle_three_way() {
    check!(r#"[5, 5, 5], idx [0, 1, 2], deltas [-5, 2, 3]"#, { let mut b = [5, 5, 5]; (settle(&mut b, [0, 1, 2], [-5, 2, 3]), b) }, (Ok(()), [0, 7, 8]));
}

#[test]
fn same_account() {
    check!(r#"transfer 1 -> 1"#, { let mut b = [1, 1]; (transfer(&mut b, 1, 1, 1), b) }, (Err(SettleError::SameAccount), [1, 1]));
}

#[test]
fn no_such_account() {
    check!(r#"transfer 0 -> 7"#, { let mut b = [1, 1]; transfer(&mut b, 0, 7, 1) }, Err(SettleError::NoSuchAccount));
}

#[test]
fn unbalanced() {
    check!(r#"settle [0, 1] by [5, -4]"#, { let mut b = [9, 9]; (settle(&mut b, [0, 1], [5, -4]), b) }, (Err(SettleError::Unbalanced), [9, 9]));
}

#[test]
fn insufficient_changes_nothing() {
    check!(r#"[3, 0, 1], settle [0, 1, 2] by [2, 1, -3]"#, { let mut b = [3, 0, 1]; (settle(&mut b, [0, 1, 2], [2, 1, -3]), b) }, (Err(SettleError::Insufficient), [3, 0, 1]));
}
