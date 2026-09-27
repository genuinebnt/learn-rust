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

#[test]
fn one_value() {
    let mut s = FreqStack::new();
    for _ in 0..3 {
        s.push(9);
    }
    check!(r#"push 9 three times; pop four times"#, (s.pop(), s.pop(), s.pop(), s.pop()), (Some(9), Some(9), Some(9), None));
}

#[test]
fn extremes() {
    let mut s = FreqStack::new();
    for x in [i32::MIN, i32::MAX, i32::MIN] {
        s.push(x);
    }
    check!(r#"push i32::MIN, i32::MAX, i32::MIN; pop three times"#, (s.pop(), s.pop(), s.pop()), (Some(i32::MIN), Some(i32::MAX), Some(i32::MIN)));
}

#[test]
fn tie_not_by_value() {
    let mut s = FreqStack::new();
    s.push(9);
    s.push(1);
    check!(r#"push 9, 1; pop"#, s.pop(), Some(1));
}

#[test]
fn negatives() {
    let mut s = FreqStack::new();
    s.push(-1);
    s.push(-2);
    check!(r#"push -1, -2; pop"#, s.pop(), Some(-2));
}

#[test]
fn refill_after_empty() {
    let mut s = FreqStack::new();
    s.push(1);
    check!(r#"push 1; pop; push 1, 2; pop"#, (s.pop(), { s.push(1); s.push(2); s.pop() }, s.pop(), s.pop()), (Some(1), Some(2), Some(1), None));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(3013);
    for _ in 0..300 {
        let mut s = FreqStack::new();
        let mut model: Vec<i32> = Vec::new();
        let mut log = Vec::new();
        let n = rng.below(24);
        for _ in 0..n {
            if rng.below(3) > 0 {
                let x = rng.int(0, 3) as i32;
                s.push(x);
                model.push(x);
                log.push(format!("push {x}"));
            } else {
                let counts: Vec<usize> = model.iter().map(|&x| model.iter().filter(|&&y| y == x).count()).collect();
                let want = counts.iter().max().map(|&b| {
                    let i = counts.iter().rposition(|&c| c == b).unwrap();
                    model.remove(i)
                });
                log.push("pop".to_string());
                check!(log.join(", "), s.pop(), want);
            }
        }
    }
}

#[test]
fn scale_200k() {
    let mut s = FreqStack::new();
    for i in 0..100_000 {
        s.push(i % 50_000);
    }
    let mut first = Vec::new();
    for _ in 0..3 {
        first.push(s.pop());
    }
    let mut rest = 0;
    while s.pop().is_some() {
        rest += 1;
    }
    check!("push i % 50000 for i in 0..100000; pop everything", (first, rest), (vec![Some(49_999), Some(49_998), Some(49_997)], 99_997));
}
