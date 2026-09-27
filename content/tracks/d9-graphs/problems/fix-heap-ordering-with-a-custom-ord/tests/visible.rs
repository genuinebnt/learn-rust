use solution::*;

#[test]
fn cheapest_first() {
    check!(r#"costs build 5, lint 1, test 3"#, run_order(vec![Job { cost: 5, name: "build" }, Job { cost: 1, name: "lint" }, Job { cost: 3, name: "test" }]), vec!["lint", "test", "build"]);
}

#[test]
fn ties() {
    check!(r#"costs b 2, a 2"#, run_order(vec![Job { cost: 2, name: "b" }, Job { cost: 2, name: "a" }]), vec!["a", "b"]);
}
