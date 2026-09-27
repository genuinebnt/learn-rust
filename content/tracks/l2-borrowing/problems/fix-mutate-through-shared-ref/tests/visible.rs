use solution::*;

#[test]
fn deposits() {
    check!(r#"balances [1, 2], amount 5"#, { let mut a = [Account { balance: 1 }, Account { balance: 2 }]; deposit_all(&mut a, 5); (a[0].balance, a[1].balance) }, (6, 7));
}

#[test]
fn negative() {
    check!(r#"balance 10, amount -3"#, { let mut a = [Account { balance: 10 }]; deposit_all(&mut a, -3); a[0].balance }, 7);
}

#[test]
fn three_accounts() {
    check!(r#"balances [0, -5, 100], amount 1"#, { let mut a = [Account { balance: 0 }, Account { balance: -5 }, Account { balance: 100 }]; deposit_all(&mut a, 1); (a[0].balance, a[1].balance, a[2].balance) }, (1, -4, 101));
}

#[test]
fn zero_amount() {
    check!(r#"balance 3, amount 0"#, { let mut a = [Account { balance: 3 }]; deposit_all(&mut a, 0); a[0].balance }, 3);
}

#[test]
fn empty() {
    check!(r#"no accounts"#, { let mut a: [Account; 0] = []; deposit_all(&mut a, 5); a.len() }, 0);
}
