use solution::*;

#[test]
fn records() {
    check!(r#"deposit 5 into 0, 7 into 1"#, { let b = Bank::new(2); b.deposit(0, 5); b.deposit(1, 7); b.audit() }, vec!["total 5", "total 12"]);
}

#[test]
fn same_account() {
    check!(r#"deposit 1 into 0 twice"#, { let b = Bank::new(1); b.deposit(0, 1); b.deposit(0, 1); b.audit() }, vec!["total 1", "total 2"]);
}

#[test]
fn three_accounts() {
    check!(r#"deposit 1, 2, 3 into accounts 0, 1, 2"#, { let b = Bank::new(3); b.deposit(0, 1); b.deposit(1, 2); b.deposit(2, 3); b.audit() }, vec!["total 1", "total 3", "total 6"]);
}

#[test]
fn withdraw() {
    check!(r#"deposit 10, then -4"#, { let b = Bank::new(1); b.deposit(0, 10); b.deposit(0, -4); b.audit() }, vec!["total 10", "total 6"]);
}

#[test]
fn no_deposits() {
    check!(r#"new bank"#, Bank::new(2).audit(), Vec::<String>::new());
}
