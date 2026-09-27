use solution::*;

#[test]
fn adds_once() {
    check!(r#"add "a" twice, "b" once"#, { let r = Registry::new(); r.add("a"); r.add("a"); r.add("b"); r.len() }, 2);
}

#[test]
fn order_kept() {
    check!(r#"add "b", "a""#, { let r = Registry::new(); r.add("b"); r.add("a"); r.add("b"); r.len() }, 2);
}

#[test]
fn single() {
    check!(r#"add "x""#, { let r = Registry::new(); r.add("x"); r.len() }, 1);
}

#[test]
fn case_sensitive() {
    check!(r#"add "a", "A""#, { let r = Registry::new(); r.add("a"); r.add("A"); r.len() }, 2);
}

#[test]
fn empty() {
    check!(r#"new registry"#, Registry::new().len(), 0);
}
