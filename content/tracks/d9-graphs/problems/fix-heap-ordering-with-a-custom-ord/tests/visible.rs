use solution::*;

#[test]
fn cheapest_first() {
    check!(r#"costs build 5, lint 1, test 3"#, run_order(vec![Job { cost: 5, name: "build" }, Job { cost: 1, name: "lint" }, Job { cost: 3, name: "test" }]), vec!["lint", "test", "build"]);
}

#[test]
fn ties() {
    check!(r#"costs b 2, a 2"#, run_order(vec![Job { cost: 2, name: "b" }, Job { cost: 2, name: "a" }]), vec!["a", "b"]);
}

#[test]
fn no_jobs() {
    check!(r#"no jobs"#, run_order(vec![]), Vec::<&str>::new());
}

#[test]
fn single_job() {
    check!(r#"costs only 4"#, run_order(vec![Job { cost: 4, name: "only" }]), vec!["only"]);
}

#[test]
fn all_same_cost() {
    check!(r#"costs c 7, a 7, b 7"#, run_order(vec![Job { cost: 7, name: "c" }, Job { cost: 7, name: "a" }, Job { cost: 7, name: "b" }]), vec!["a", "b", "c"]);
}
