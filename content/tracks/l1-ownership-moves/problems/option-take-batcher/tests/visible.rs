use solution::*;

#[test]
fn fills() {
    check!(r#"size 2, push 1, 2, 3"#, { let mut b = Batcher::new(2); (b.push(1), b.push(2), b.push(3)) }, (None, Some(vec![1, 2]), None));
}

#[test]
fn flush_rest() {
    check!(r#"size 3, push 7, flush twice"#, { let mut b = Batcher::new(3); b.push(7); (b.flush(), b.flush()) }, (Some(vec![7]), None));
}

#[test]
fn exact_multiple() {
    check!(r#"size 2, push 1, 2, 3, 4"#, { let mut b = Batcher::new(2); (b.push(1), b.push(2), b.push(3), b.push(4)) }, (None, Some(vec![1, 2]), None, Some(vec![3, 4])));
}

#[test]
fn flush_nothing() {
    check!(r#"size 2, nothing pushed"#, Batcher::new(2).flush(), None);
}

#[test]
fn flush_after_batch() {
    check!(r#"size 1, push 5, flush"#, { let mut b = Batcher::new(1); (b.push(5), b.flush()) }, (Some(vec![5]), None));
}
