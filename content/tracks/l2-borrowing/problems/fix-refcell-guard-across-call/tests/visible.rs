use solution::*;

#[test]
fn records() {
    check!(r#"deposit 5 into 0, 7 into 1"#, { let b = Bank::new(2); b.deposit(0, 5); b.deposit(1, 7); b.audit() }, vec!["total 5", "total 12"]);
}

#[test]
fn same_account() {
    check!(r#"deposit 1 into 0 twice"#, { let b = Bank::new(1); b.deposit(0, 1); b.deposit(0, 1); b.audit() }, vec!["total 1", "total 2"]);
}
