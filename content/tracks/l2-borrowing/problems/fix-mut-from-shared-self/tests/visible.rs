use solution::*;

#[test]
fn edit_top() {
    check!(r#"push 1, 2; add 10 to the top"#, { let mut s = Stack::new(); s.push(1); s.push(2); *s.top_mut().unwrap() += 10; s.top_mut().copied() }, Some(12));
}

#[test]
fn empty() {
    check!(r#"new stack"#, Stack::new().top_mut().is_none(), true);
}
