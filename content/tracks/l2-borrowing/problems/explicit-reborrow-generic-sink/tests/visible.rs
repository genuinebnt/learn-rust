use solution::*;

#[test]
fn twice() {
    check!(r#"xs = [7, 8]"#, { let mut v = vec![]; emit_twice(&mut v, &[7, 8]); v }, vec![7, 8, 7, 8]);
}

#[test]
fn appends() {
    check!(r#"sink = [0], xs = [1]"#, { let mut v = vec![0]; emit_twice(&mut v, &[1]); v }, vec![0, 1, 1]);
}
