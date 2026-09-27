use solution::*;

#[test]
fn ok() {
    check!(r#"n = 4, deps = [(2, 0), (0, 1), (3, 1)]"#, build_order(4, &[(2, 0), (0, 1), (3, 1)]), Ok(vec![2, 0, 3, 1]));
}

#[test]
fn stuck() {
    check!(r#"n = 4, deps = [(0, 1), (1, 2), (2, 1), (2, 3)]"#, build_order(4, &[(0, 1), (1, 2), (2, 1), (2, 3)]), Err(vec![1, 2, 3]));
}

#[test]
fn single() {
    check!(r#"n = 1, deps = []"#, build_order(1, &[]), Ok(vec![0]));
}

#[test]
fn smallest_ready_not_first_ready() {
    check!(r#"n = 4, deps = [(0, 3), (1, 2)]"#, build_order(4, &[(0, 3), (1, 2)]), Ok(vec![0, 1, 2, 3]));
}

#[test]
fn self_dependency() {
    check!(r#"n = 3, deps = [(1, 1)]"#, build_order(3, &[(1, 1)]), Err(vec![1]));
}
