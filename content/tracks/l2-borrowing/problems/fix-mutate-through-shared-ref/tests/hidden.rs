use solution::*;

#[test]
fn reward_none_selected() {
    check!(r#"balances [1, 2], min 10"#, { let mut v = vec![Account { id: 1, balance: 1 }, Account { id: 2, balance: 2 }]; (reward(&mut v, 10, 50), v[0].balance, v[1].balance) }, (vec![], 1, 2));
}

#[test]
fn reward_empty() {
    check!(r#"no accounts"#, reward(&mut [], 0, 10), vec![]);
}

#[test]
fn reward_at_min() {
    check!(r#"balance 100, min 100, 1%"#, { let mut v = vec![Account { id: 7, balance: 100 }]; (reward(&mut v, 100, 1), v[0].balance) }, (vec![7], 101));
}

#[test]
fn zero_percent() {
    check!(r#"balance 99, 0%"#, { let mut v = vec![Account { id: 1, balance: 99 }]; reward(&mut v, 0, 0); v[0].balance }, 99);
}

#[test]
fn small_balance_no_interest() {
    check!(r#"balance 9, 10%"#, { let mut v = vec![Account { id: 1, balance: 9 }]; reward(&mut v, 0, 10); v[0].balance }, 9);
}

#[test]
fn top_up_negative() {
    check!(r#"to 5, from 5, amount -3"#, { let (mut to, mut from) = (Account { id: 1, balance: 5 }, Account { id: 2, balance: 5 }); top_up(&mut to, &mut from, -3); (to.balance, from.balance) }, (2, 8));
}

#[test]
fn richest_empty() {
    check!(r#"no accounts"#, richest_id(&[]), None);
}

#[test]
fn richest_negative() {
    check!(r#"balances [-5, -2, -9]"#, richest_id(&vec![Account { id: 1, balance: -5 }, Account { id: 2, balance: -2 }, Account { id: 3, balance: -9 }]), Some(2));
}

#[test]
fn keep_richest_tie() {
    check!(r#"richest 4, candidate 4"#, { let (a, b) = (Account { id: 1, balance: 4 }, Account { id: 2, balance: 4 }); let mut r = &a; keep_richest(&mut r, &b); r.id }, 1);
}

#[test]
fn large_balances() {
    check!(r#"balance 10^15, 3%"#, { let mut v = vec![Account { id: 1, balance: 1000000000000000 }]; reward(&mut v, 0, 3); v[0].balance }, 1030000000000000);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6205);
    for _ in 0..300 {
        let n = rng.below(7);
        let balances: Vec<i64> = rng.vec(n, -500, 500);
        let min = rng.int(-500, 500);
        let pct = rng.int(0, 30);
        let mut v: Vec<Account> = balances.iter().enumerate().map(|(i, &b)| Account { id: i as u32, balance: b }).collect();
        let want_ids: Vec<u32> = v.iter().filter(|a| a.balance >= min).map(|a| a.id).collect();
        let want: Vec<i64> = balances.iter().map(|&b| if b >= min { b + b * pct / 100 } else { b }).collect();
        let ids = reward(&mut v, min, pct);
        let got: Vec<i64> = v.iter().map(|a| a.balance).collect();
        check!(format!("balances {balances:?}, min {min}, {pct}%"), (ids, got), (want_ids, want));
    }
}
