use solution::*;

#[test]
fn duplicates() {
    let mut s = MinStack::new();
    s.push(1);
    s.push(1);
    check!(r#"push 1, 1; pop; min"#, (s.pop(), s.min()), (Some(1), Some(1)));
}

#[test]
fn extremes() {
    let mut s = MinStack::new();
    s.push(i32::MAX);
    s.push(i32::MIN);
    check!(r#"push i32::MAX, i32::MIN"#, s.min(), Some(i32::MIN));
}
