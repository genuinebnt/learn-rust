use solution::*;

#[test]
fn edit_top() {
    check!(r#"push 1, 2; add 10 to the top"#, { let mut s = Stack::new(); s.push(1); s.push(2); *s.top_mut().unwrap() += 10; s.top_mut().copied() }, Some(12));
}

#[test]
fn empty() {
    check!(r#"new stack"#, Stack::new().top_mut().is_none(), true);
}

#[test]
fn push_after_edit() {
    check!(r#"push 1; set top to 7; push 2"#, { let mut s = Stack::new(); s.push(1); *s.top_mut().unwrap() = 7; s.push(2); s.items_for_test() }, vec![7, 2]);
}

#[test]
fn only_top_changes() {
    check!(r#"push 5, 6; set top to 0"#, { let mut s = Stack::new(); s.push(5); s.push(6); if let Some(t) = s.top_mut() { *t = 0; } s.items_for_test() }, vec![5, 0]);
}

#[test]
fn single() {
    check!(r#"push 3; double the top"#, { let mut s = Stack::new(); s.push(3); *s.top_mut().unwrap() *= 2; s.items_for_test() }, vec![6]);
}
