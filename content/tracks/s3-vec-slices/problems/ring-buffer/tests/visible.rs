use solution::*;

#[test]
fn not_full() {
    check!(r#"capacity 3, push 1, 2"#, { let mut r = Ring::with_capacity(3); r.push(1); r.push(2); r.iter().copied().collect::<Vec<_>>() }, vec![1, 2]);
}

#[test]
fn evicts_oldest() {
    check!(r#"capacity 2, push 1, 2, 3"#, { let mut r = Ring::with_capacity(2); r.push(1); r.push(2); let e = r.push(3); (e, r.iter().copied().collect::<Vec<_>>()) }, (Some(1), vec![2, 3]));
}
