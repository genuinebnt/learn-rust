use solution::*;

#[test]
fn empty() {
    check!(r#"xs = []"#, { let mut v = vec![1]; emit_twice(&mut v, &[]); v }, vec![1]);
}
