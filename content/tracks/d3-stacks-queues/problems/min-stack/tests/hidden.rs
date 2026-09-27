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

#[test]
fn pop_to_empty() {
    let mut s = MinStack::new();
    s.push(4);
    check!(r#"push 4; pop, pop, min, top"#, (s.pop(), s.pop(), s.min(), s.top()), (Some(4), None, None, None));
}

#[test]
fn push_after_empty() {
    let mut s = MinStack::new();
    s.push(5);
    s.pop();
    s.push(7);
    check!(r#"push 5; pop; push 7; min"#, (s.min(), s.top()), (Some(7), Some(7)));
}

#[test]
fn descending() {
    let mut s = MinStack::new();
    for x in [5, 4, 3, 2, 1] {
        s.push(x);
    }
    let mins: Vec<Option<i32>> = (0..5).map(|_| { s.pop(); s.min() }).collect();
    check!(r#"push 5, 4, 3, 2, 1; min after each pop"#, mins, vec![Some(2), Some(3), Some(4), Some(5), None]);
}

#[test]
fn ascending() {
    let mut s = MinStack::new();
    for x in [1, 2, 3] {
        s.push(x);
    }
    let mins: Vec<Option<i32>> = (0..3).map(|_| { s.pop(); s.min() }).collect();
    check!(r#"push 1, 2, 3; min after each pop"#, mins, vec![Some(1), Some(1), None]);
}

#[test]
fn min_twice() {
    let mut s = MinStack::new();
    s.push(i32::MIN);
    s.push(i32::MIN);
    check!(r#"push i32::MIN twice; pop; min"#, (s.pop(), s.min()), (Some(i32::MIN), Some(i32::MIN)));
}

#[test]
fn negatives() {
    let mut s = MinStack::new();
    s.push(-1);
    s.push(-5);
    s.push(-3);
    check!(r#"push -1, -5, -3; min, pop, min, pop, min"#, (s.min(), s.pop(), s.min(), s.pop(), s.min()), (Some(-5), Some(-3), Some(-5), Some(-5), Some(-1)));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(3004);
    for _ in 0..300 {
        let mut s = MinStack::new();
        let mut model: Vec<i32> = Vec::new();
        let mut log = Vec::new();
        let n = rng.below(20);
        for _ in 0..n {
            if rng.below(3) > 0 {
                let x = rng.int(-9, 9) as i32;
                s.push(x);
                model.push(x);
                log.push(format!("push {x}"));
            } else {
                log.push("pop".to_string());
                check!(log.join(", "), s.pop(), model.pop());
            }
            check!(log.join(", "), (s.top(), s.min()), (model.last().copied(), model.iter().min().copied()));
        }
    }
}

#[test]
fn scale_200k() {
    let mut s = MinStack::new();
    let mut sum = 0i64;
    for i in 0..200_000 {
        s.push(200_000 - i);
        sum += i64::from(s.min().unwrap_or(0));
    }
    for _ in 0..100_000 {
        s.pop();
        sum += i64::from(s.min().unwrap_or(0));
    }
    check!("push 200000 down to 1 (min after each), then pop 100000 (min after each)", sum, 25_000_250_000);
}
