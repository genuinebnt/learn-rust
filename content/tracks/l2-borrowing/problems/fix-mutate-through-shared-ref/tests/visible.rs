use solution::*;

#[test]
fn deposits() {
    check!(r#"balances [1, 2], amount 5"#, { let mut a = [Account { balance: 1 }, Account { balance: 2 }]; deposit_all(&mut a, 5); (a[0].balance, a[1].balance) }, (6, 7));
}

#[test]
fn negative() {
    check!(r#"balance 10, amount -3"#, { let mut a = [Account { balance: 10 }]; deposit_all(&mut a, -3); a[0].balance }, 7);
}
