use solution::*;

#[test]
fn example() {
    let mut s = FreqStack::new();
    for x in [5, 7, 5, 7, 4, 5] {
        s.push(x);
    }
    check!(r#"push 5,7,5,7,4,5; pop four times"#, (s.pop(), s.pop(), s.pop(), s.pop()), (Some(5), Some(7), Some(5), Some(4)));
}

#[test]
fn empty() {
    check!(r#"new stack"#, FreqStack::new().pop(), None);
}
