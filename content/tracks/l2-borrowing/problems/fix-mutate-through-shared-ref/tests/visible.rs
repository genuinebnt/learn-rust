use solution::*;

#[test]
fn reward_pays_selected() {
    check!(r#"balances [100, 50, 300], min 100, 10%"#, { let mut v = vec![Account { id: 1, balance: 100 }, Account { id: 2, balance: 50 }, Account { id: 3, balance: 300 }]; let ids = reward(&mut v, 100, 10); (ids, v.iter().map(|a| a.balance).collect::<Vec<_>>()) }, (vec![1, 3], vec![110, 50, 330]));
}

#[test]
fn interest_rounds_toward_zero() {
    check!(r#"balances [15, -15], min -100, 10%"#, { let mut v = vec![Account { id: 1, balance: 15 }, Account { id: 2, balance: -15 }]; reward(&mut v, -100, 10); (v[0].balance, v[1].balance) }, (16, -16));
}

#[test]
fn top_up_moves_funds() {
    check!(r#"to 5, from 20, amount 7"#, { let (mut to, mut from) = (Account { id: 1, balance: 5 }, Account { id: 2, balance: 20 }); top_up(&mut to, &mut from, 7); (to.balance, from.balance) }, (12, 13));
}

#[test]
fn richest_first_on_tie() {
    check!(r#"balances [3, 9, 9]"#, richest_id(&vec![Account { id: 1, balance: 3 }, Account { id: 2, balance: 9 }, Account { id: 3, balance: 9 }]), Some(2));
}

#[test]
fn keep_richest_repoints() {
    check!(r#"richest 4, candidate 8"#, { let (a, b) = (Account { id: 1, balance: 4 }, Account { id: 2, balance: 8 }); let mut r = &a; keep_richest(&mut r, &b); r.id }, 2);
}

#[test]
fn pay_interest_direct() {
    check!(r#"two selected accounts 200, 1000; 5%"#, { let (mut a, mut b) = (Account { id: 1, balance: 200 }, Account { id: 2, balance: 1000 }); pay_interest(&mut [&mut a, &mut b], 5); (a.balance, b.balance) }, (210, 1050));
}
