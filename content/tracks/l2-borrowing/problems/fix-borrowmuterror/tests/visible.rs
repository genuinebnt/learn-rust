use solution::*;

#[test]
fn adds_once() {
    check!(r#"add "a" twice, "b" once"#, { let r = Registry::new(); r.add("a"); r.add("a"); r.add("b"); r.len() }, 2);
}

#[test]
fn order_kept() {
    check!(r#"add "b", "a""#, { let r = Registry::new(); r.add("b"); r.add("a"); r.add("b"); r.len() }, 2);
}
