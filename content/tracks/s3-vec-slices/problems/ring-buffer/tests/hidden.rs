use solution::*;

#[test]
fn wraps_many_times() {
    check!(r#"capacity 3, push 0..10"#, { let mut r = Ring::with_capacity(3); for i in 0..10 { r.push(i); } (r.len(), r.iter().copied().collect::<Vec<_>>()) }, (3, vec![7, 8, 9]));
}

#[test]
fn capacity_one() {
    check!(r#"capacity 1, push "a", "b""#, { let mut r = Ring::with_capacity(1); r.push("a"); (r.push("b"), r.iter().copied().collect::<Vec<_>>()) }, (Some("a"), vec!["b"]));
}
