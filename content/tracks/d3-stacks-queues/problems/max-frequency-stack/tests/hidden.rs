use solution::*;

#[test]
fn drains() {
    let mut s = FreqStack::new();
    for x in [5, 7, 5, 7, 4, 5] {
        s.push(x);
    }
    let out: Vec<Option<i32>> = (0..7).map(|_| s.pop()).collect();
    check!(r#"push 5,7,5,7,4,5; pop seven times"#, out, vec![Some(5), Some(7), Some(5), Some(4), Some(7), Some(5), None]);
}

#[test]
fn push_after_pop() {
    let mut s = FreqStack::new();
    s.push(1);
    s.push(1);
    let a = s.pop();
    s.push(2);
    let b = s.pop();
    let c = s.pop();
    check!(r#"push 1,1; pop; push 2; pop; pop"#, (a, b, c), (Some(1), Some(2), Some(1)));
}
