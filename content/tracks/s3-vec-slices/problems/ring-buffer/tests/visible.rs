use solution::*;

#[test]
fn not_full() {
    check!(r#"capacity 3, push 1, 2"#, { let mut r = Ring::with_capacity(3); r.push(1); r.push(2); r.iter().copied().collect::<Vec<_>>() }, vec![1, 2]);
}

#[test]
fn evicts_oldest() {
    check!(r#"capacity 2, push 1, 2, 3"#, { let mut r = Ring::with_capacity(2); r.push(1); r.push(2); let e = r.push(3); (e, r.iter().copied().collect::<Vec<_>>()) }, (Some(1), vec![2, 3]));
}

#[test]
fn exactly_full() {
    check!(r#"capacity 3, push 1, 2, 3"#, { let mut r = Ring::with_capacity(3); let e = (r.push(1), r.push(2), r.push(3)); (e, r.iter().copied().collect::<Vec<_>>()) }, ((None, None, None), vec![1, 2, 3]));
}

#[test]
fn len_stops_at_capacity() {
    check!(r#"capacity 2, push 1, 2, 3"#, { let mut r = Ring::with_capacity(2); r.push(1); r.push(2); r.push(3); r.len() }, 2);
}

#[test]
fn evictions_in_order() {
    check!(r#"capacity 2, push 1, 2, 3, 4"#, { let mut r = Ring::with_capacity(2); r.push(1); r.push(2); (r.push(3), r.push(4)) }, (Some(1), Some(2)));
}
