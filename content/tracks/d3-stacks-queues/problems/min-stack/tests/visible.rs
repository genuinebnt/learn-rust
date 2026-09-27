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

#[test]
fn min_below_top() {
    let mut s = MinStack::new();
    s.push(3);
    s.push(5);
    check!(r#"push 3, 5; top, min"#, (s.top(), s.min()), (Some(5), Some(3)));
}

#[test]
fn repeated_min() {
    let mut s = MinStack::new();
    s.push(2);
    s.push(1);
    s.push(1);
    check!(r#"push 2, 1, 1; pop; min"#, (s.pop(), s.min()), (Some(1), Some(1)));
}

#[test]
fn min_restored() {
    let mut s = MinStack::new();
    s.push(1);
    s.push(0);
    check!(r#"push 1, 0; pop; min"#, (s.pop(), s.min()), (Some(0), Some(1)));
}
