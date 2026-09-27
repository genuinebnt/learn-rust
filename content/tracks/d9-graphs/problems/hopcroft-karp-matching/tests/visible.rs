use solution::*;

#[test]
fn two() {
    check!(r#"left = 3, right = 3, edges = [(0,0), (0,1), (1,0), (2,1)]"#, max_matching(3, 3, &[(0, 0), (0, 1), (1, 0), (2, 1)]), 2);
}

#[test]
fn rematch() {
    check!(r#"left = 2, right = 2, edges = [(0,0), (0,1), (1,0)]"#, max_matching(2, 2, &[(0, 0), (0, 1), (1, 0)]), 2);
}
