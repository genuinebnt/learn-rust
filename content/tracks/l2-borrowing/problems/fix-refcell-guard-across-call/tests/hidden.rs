use solution::*;

#[test]
fn negative() {
    check!(r#"deposit -3"#, { let b = Bank::new(1); b.deposit(0, -3); b.audit() }, vec!["total -3"]);
}

#[test]
fn zero_deposit() {
    check!(r#"deposit 0"#, { let b = Bank::new(1); b.deposit(0, 0); b.audit() }, vec!["total 0"]);
}

#[test]
fn large() {
    check!(r#"deposit i64::MAX / 2 into two accounts"#, { let b = Bank::new(2); b.deposit(0, i64::MAX / 2); b.deposit(1, i64::MAX / 2); b.audit()[1].clone() }, format!("total {}", i64::MAX - 1));
}

#[test]
fn many() {
    check!(r#"1000 deposits of 1"#, { let b = Bank::new(4); for i in 0..1000 { b.deposit(i % 4, 1); } let a = b.audit(); (a.len(), a[999].clone()) }, (1000, "total 1000".to_string()));
}

#[test]
fn other_accounts_count() {
    check!(r#"deposit 5 into 0, then 1 into 2"#, { let b = Bank::new(3); b.deposit(0, 5); b.deposit(2, 1); b.audit() }, vec!["total 5", "total 6"]);
}

#[test]
fn back_to_zero() {
    check!(r#"deposit 7, then -7"#, { let b = Bank::new(2); b.deposit(1, 7); b.deposit(1, -7); b.audit() }, vec!["total 7", "total 0"]);
}

#[test]
fn audit_is_a_copy() {
    check!(r#"read the audit twice"#, { let b = Bank::new(1); b.deposit(0, 2); let first = b.audit(); b.deposit(0, 2); (first.len(), b.audit().len()) }, (1, 2));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2032);
    for _ in 0..300 {
        let k = 1 + rng.below(4);
        let b = Bank::new(k);
        let mut total = 0i64;
        let mut want = Vec::new();
        let mut log = Vec::new();
        let n = rng.below(8);
        for _ in 0..n {
            let i = rng.below(k);
            let amount = rng.int(-50, 50);
            b.deposit(i, amount);
            total += amount;
            want.push(format!("total {total}"));
            log.push(format!("{amount} into {i}"));
        }
        check!(format!("{k} accounts; {}", log.join(", ")), b.audit(), want);
    }
}
