use solution::*;

#[test]
fn no_deps() {
    check!(r#"n = 3, deps = []"#, build_order(3, &[]), Ok(vec![0, 1, 2]));
}

#[test]
fn smallest_first() {
    check!(r#"n = 3, deps = [(2, 1)]"#, build_order(3, &[(2, 1)]), Ok(vec![0, 2, 1]));
}

#[test]
fn all_stuck() {
    check!(r#"n = 2, deps = [(0, 1), (1, 0)]"#, build_order(2, &[(0, 1), (1, 0)]), Err(vec![0, 1]));
}
