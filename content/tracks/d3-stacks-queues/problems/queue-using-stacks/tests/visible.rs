use solution::*;

#[test]
fn fifo() {
    let mut q = TwoStackQueue::new();
    q.push(1);
    q.push(2);
    check!(r#"push 1, 2; peek, pop; push 3; pop, pop, pop"#, (q.peek(), q.pop(), { q.push(3); q.pop() }, q.pop(), q.pop()), (Some(1), Some(1), Some(2), Some(3), None));
}

#[test]
fn len() {
    let mut q = TwoStackQueue::new();
    for x in [4, 5, 6] {
        q.push(x);
    }
    q.pop();
    check!(r#"push 3 values, pop 1"#, (q.len(), q.is_empty()), (2, false));
}

#[test]
fn leetcode_example() {
    let mut q = TwoStackQueue::new();
    q.push(1);
    q.push(2);
    check!(r#"push 1, push 2, peek, pop, empty"#, (q.peek(), q.pop(), q.is_empty()), (Some(1), Some(1), false));
}

#[test]
fn empty_queue() {
    let mut q = TwoStackQueue::new();
    check!(r#"new queue"#, (q.peek(), q.pop(), q.len(), q.is_empty()), (None, None, 0, true));
}

#[test]
fn push_between_pops() {
    let mut q = TwoStackQueue::new();
    q.push(1);
    q.push(2);
    let a = q.pop();
    q.push(3);
    q.push(4);
    check!(r#"push 1, 2; pop; push 3, 4; pop, pop, pop"#, (a, q.pop(), q.pop(), q.pop()), (Some(1), Some(2), Some(3), Some(4)));
}
