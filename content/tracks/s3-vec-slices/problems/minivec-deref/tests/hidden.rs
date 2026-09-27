use solution::*;

#[test]
fn empty_slice() {
    check!(r#"new MiniVec"#, MiniVec::<String>::new().as_slice().len(), 0);
}

#[test]
fn range_index() {
    check!(r#"push 10, 20, 30"#, { let mut v = MiniVec::new(); v.push(10); v.push(20); v.push(30); v[1..].to_vec() }, vec![20, 30]);
}

#[test]
fn mutate_through_slice() {
    check!(r#"push 1, 2"#, { let mut v = MiniVec::new(); v.push(1); v.push(2); for x in v.iter_mut() { *x *= 5; } v.as_slice().to_vec() }, vec![5, 10]);
}
