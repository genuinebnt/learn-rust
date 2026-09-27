use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, push_sum(vec![]), vec![0]);
}

#[test]
fn same_buffer() {
    check!(r#"v with capacity 10"#, { let mut v = Vec::with_capacity(10); v.push(5); let p = v.as_ptr(); let out = push_sum(v); out.as_ptr() == p }, true);
}
