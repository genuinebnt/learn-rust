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

#[test]
fn tie_most_recent() {
    let mut s = FreqStack::new();
    s.push(1);
    s.push(2);
    check!(r#"push 1, 2; pop, pop"#, (s.pop(), s.pop()), (Some(2), Some(1)));
}

#[test]
fn frequency_drops() {
    let mut s = FreqStack::new();
    for x in [3, 3, 4] {
        s.push(x);
    }
    check!(r#"push 3, 3, 4; pop three times"#, (s.pop(), s.pop(), s.pop()), (Some(3), Some(4), Some(3)));
}

#[test]
fn frequency_beats_recency() {
    let mut s = FreqStack::new();
    for x in [1, 1, 2] {
        s.push(x);
    }
    check!(r#"push 1, 1, 2; pop"#, s.pop(), Some(1));
}
