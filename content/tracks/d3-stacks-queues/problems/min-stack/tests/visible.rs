use solution::*;

#[test]
fn tracks_min() {
    let mut s = MinStack::new();
    s.push(-2);
    s.push(0);
    s.push(-3);
    check!(r#"push -2, 0, -3; min; pop; top; min"#, (s.min(), s.pop(), s.top(), s.min()), (Some(-3), Some(-3), Some(0), Some(-2)));
}

#[test]
fn empty() {
    let mut s = MinStack::new();
    check!(r#"new stack"#, (s.min(), s.top(), s.pop()), (None, None, None));
}
