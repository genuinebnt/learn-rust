use solution::*;

#[test]
fn negative() {
    check!(r#"deposit -3"#, { let b = Bank::new(1); b.deposit(0, -3); b.audit() }, vec!["total -3"]);
}
