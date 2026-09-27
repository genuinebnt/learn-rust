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
