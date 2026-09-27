use solution::*;

#[test]
fn single() {
    check!(r#"balance 7, amount 3"#, { let mut a = [Account { balance: 7 }]; deposit_all(&mut a, 3); a[0].balance }, 10);
}

#[test]
fn to_max() {
    check!(r#"balance i64::MAX - 1, amount 1"#, { let mut a = [Account { balance: i64::MAX - 1 }]; deposit_all(&mut a, 1); a[0].balance }, i64::MAX);
}

#[test]
fn to_min() {
    check!(r#"balance 0, amount i64::MIN"#, { let mut a = [Account { balance: 0 }]; deposit_all(&mut a, i64::MIN); a[0].balance }, i64::MIN);
}

#[test]
fn same_balances() {
    check!(r#"balances [2, 2, 2], amount 2"#, { let mut a = [Account { balance: 2 }, Account { balance: 2 }, Account { balance: 2 }]; deposit_all(&mut a, 2); (a[0].balance, a[1].balance, a[2].balance) }, (4, 4, 4));
}

#[test]
fn in_a_vec() {
    check!(r#"1000 accounts at 0, amount 3"#, { let mut a: Vec<Account> = (0..1000).map(|_| Account { balance: 0 }).collect(); deposit_all(&mut a, 3); a.iter().map(|x| x.balance).sum::<i64>() }, 3000);
}

#[test]
fn called_twice() {
    check!(r#"balance 0; +1 then +2"#, { let mut a = [Account { balance: 0 }]; deposit_all(&mut a, 1); deposit_all(&mut a, 2); a[0].balance }, 3);
}

#[test]
fn sub_slice() {
    check!(r#"balances [0, 0, 0]; deposit into [1..]"#, { let mut a = [Account { balance: 0 }, Account { balance: 0 }, Account { balance: 0 }]; deposit_all(&mut a[1..], 4); (a[0].balance, a[1].balance, a[2].balance) }, (0, 4, 4));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2005);
    for _ in 0..300 {
        let n = rng.below(10);
        let start: Vec<i64> = rng.vec(n, -1000, 1000);
        let amount = rng.int(-1000, 1000);
        let mut a: Vec<Account> = start.iter().map(|&b| Account { balance: b }).collect();
        deposit_all(&mut a, amount);
        let got: Vec<i64> = a.iter().map(|x| x.balance).collect();
        let want: Vec<i64> = start.iter().map(|b| b + amount).collect();
        check!(format!("balances {start:?}, amount {amount}"), got, want);
    }
}
