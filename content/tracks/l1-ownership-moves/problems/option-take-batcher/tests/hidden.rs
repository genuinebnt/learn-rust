use solution::*;

#[test]
fn size_one() {
    check!(r#"size 1"#, { let mut b = Batcher::new(1); (b.push(5), b.flush()) }, (Some(vec![5]), None));
}

#[test]
fn flush_empty() {
    check!(r#"nothing pushed"#, Batcher::new(4).flush(), None);
}
