use solution::*;

#[test]
fn mixed() {
    check!(r#"costs c 1, a 2, b 1, d 0"#, run_order(vec![Job { cost: 1, name: "c" }, Job { cost: 2, name: "a" }, Job { cost: 1, name: "b" }, Job { cost: 0, name: "d" }]), vec!["d", "b", "c", "a"]);
}

#[test]
fn consistent_with_eq() {
    check!(r#"two jobs, same cost, different names"#, Job { cost: 1, name: "a" }.cmp(&Job { cost: 1, name: "b" }) != std::cmp::Ordering::Equal, true);
}
