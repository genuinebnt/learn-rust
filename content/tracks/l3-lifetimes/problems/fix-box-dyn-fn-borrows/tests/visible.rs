use solution::*;

#[test]
fn make_filter_example() {
    let allowed = vec!["a", "b"];
    let f = make_filter(&allowed);
    check!(r#"allowed ["a", "b"]: test a, c"#, (f("a"), f("c")), (true, false));
}

#[test]
fn checks_borrow_locals() {
    let min = 3;
    let list = vec![String::from("abc")];
    let mut c = Checks::new();
    c.add("long", |w| w.len() >= min);
    c.add("listed", |w| list.iter().any(|x| x == w));
    check!(r#"checks: min length from a local, in a local list"#, c.failures("xy"), vec!["long", "listed"]);
}

#[test]
fn count_passing_borrowed_closure() {
    let limit = 3;
    check!(r#"count words shorter than a local limit"#, count_passing(&["a", "abc", "ab"], &|w| w.len() < limit), 2);
}

#[test]
fn labels_example() {
    let names = vec![String::from("x"), String::from("yz")];
    check!(r#"labels of ["x", "yz"]"#, labels(&names).iter().map(|l| l.to_string()).collect::<Vec<_>>(), vec!["x".to_string(), "yz".to_string()]);
}

#[test]
fn no_checks() {
    check!(r#"no checks: failures of anything"#, Checks::new().failures("w").len(), 0);
}
