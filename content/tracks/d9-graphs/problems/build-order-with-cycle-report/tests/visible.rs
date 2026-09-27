use solution::*;

#[test]
fn ok() {
    check!(r#"n = 4, deps = [(2, 0), (0, 1), (3, 1)]"#, build_order(4, &[(2, 0), (0, 1), (3, 1)]), Ok(vec![2, 0, 3, 1]));
}

#[test]
fn stuck() {
    check!(r#"n = 4, deps = [(0, 1), (1, 2), (2, 1), (2, 3)]"#, build_order(4, &[(0, 1), (1, 2), (2, 1), (2, 3)]), Err(vec![1, 2, 3]));
}
