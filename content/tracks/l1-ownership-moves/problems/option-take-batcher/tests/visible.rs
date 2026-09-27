use solution::*;

#[test]
fn fills() {
    check!(r#"size 2, push 1, 2, 3"#, { let mut b = Batcher::new(2); (b.push(1), b.push(2), b.push(3)) }, (None, Some(vec![1, 2]), None));
}

#[test]
fn flush_rest() {
    check!(r#"size 3, push 7, flush twice"#, { let mut b = Batcher::new(3); b.push(7); (b.flush(), b.flush()) }, (Some(vec![7]), None));
}
