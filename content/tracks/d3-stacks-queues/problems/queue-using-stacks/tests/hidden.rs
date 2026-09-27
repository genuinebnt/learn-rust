use solution::*;

#[test]
fn empty() {
    let mut q = TwoStackQueue::new();
    check!(r#"new queue"#, (q.peek(), q.pop(), q.is_empty()), (None, None, true));
}

#[test]
fn million_ops() {
    let mut q = TwoStackQueue::new();
    let mut last = None;
    for i in 0..1_000_000 {
        q.push(i);
        if i % 2 == 1 {
            last = q.pop();
        }
    }
    check!(r#"10⁶ pushes interleaved with pops"#, (last, q.len()), (Some(499_999), 500_000));
}

#[test]
fn peek_twice() {
    let mut q = TwoStackQueue::new();
    q.push(7);
    check!(r#"push 7; peek, peek, len"#, (q.peek(), q.peek(), q.len()), (Some(7), Some(7), 1));
}

#[test]
fn drain_then_reuse() {
    let mut q = TwoStackQueue::new();
    q.push(1);
    check!(r#"push 1; pop; pop; push 2; peek"#, (q.pop(), q.pop(), { q.push(2); q.peek() }, q.len()), (Some(1), None, Some(2), 1));
}

#[test]
fn extremes() {
    let mut q = TwoStackQueue::new();
    q.push(i32::MIN);
    q.push(i32::MAX);
    check!(r#"push i32::MIN, i32::MAX; pop, pop"#, (q.pop(), q.pop()), (Some(i32::MIN), Some(i32::MAX)));
}

#[test]
fn duplicates() {
    let mut q = TwoStackQueue::new();
    for x in [5, 5, 6] {
        q.push(x);
    }
    check!(r#"push 5, 5, 6; pop three times"#, (q.pop(), q.pop(), q.pop()), (Some(5), Some(5), Some(6)));
}

#[test]
fn len_counts_both_stacks() {
    let mut q = TwoStackQueue::new();
    q.push(1);
    q.push(2);
    q.peek();
    q.push(3);
    check!(r#"push 1, 2; peek; push 3"#, (q.len(), q.is_empty()), (3, false));
}

#[test]
fn random_vs_vecdeque() {
    let mut rng = anneal_prelude::Rng::new(3002);
    for _ in 0..300 {
        let mut q = TwoStackQueue::new();
        let mut model = std::collections::VecDeque::new();
        let mut log = Vec::new();
        let n = rng.below(20);
        for _ in 0..n {
            match rng.below(3) {
                0 => {
                    let x = rng.int(-9, 9) as i32;
                    q.push(x);
                    model.push_back(x);
                    log.push(format!("push {x}"));
                }
                1 => {
                    log.push("pop".to_string());
                    check!(log.join(", "), q.pop(), model.pop_front());
                }
                _ => {
                    log.push("peek".to_string());
                    check!(log.join(", "), q.peek(), model.front().copied());
                }
            }
            check!(log.join(", "), (q.len(), q.is_empty()), (model.len(), model.is_empty()));
        }
    }
}

#[test]
fn scale_peek_pop_200k() {
    let mut q = TwoStackQueue::new();
    for i in 0..200_000 {
        q.push(i);
    }
    let mut sum = 0i64;
    for _ in 0..100_000 {
        sum += i64::from(q.peek().unwrap_or(0));
        q.pop();
        q.push(-1);
    }
    check!("push 0..200000; then 100000 × (peek, pop, push -1)", (sum, q.len(), q.peek()), (4_999_950_000, 200_000, Some(100_000)));
}
