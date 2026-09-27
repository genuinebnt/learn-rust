use solution::*;

#[test]
fn two() {
    check!(r#"left = 3, right = 3, edges = [(0,0), (0,1), (1,0), (2,1)]"#, max_matching(3, 3, &[(0, 0), (0, 1), (1, 0), (2, 1)]), 2);
}

#[test]
fn rematch() {
    check!(r#"left = 2, right = 2, edges = [(0,0), (0,1), (1,0)]"#, max_matching(2, 2, &[(0, 0), (0, 1), (1, 0)]), 2);
}

#[test]
fn one_edge() {
    check!(r#"left = 1, right = 1, edges = [(0,0)]"#, max_matching(1, 1, &[(0, 0)]), 1);
}

#[test]
fn many_want_the_same_right_node() {
    check!(r#"left = 3, right = 1, edges = [(0,0), (1,0), (2,0)]"#, max_matching(3, 1, &[(0, 0), (1, 0), (2, 0)]), 1);
}

#[test]
fn empty_left_side() {
    check!(r#"left = 0, right = 2, edges = []"#, max_matching(0, 2, &[]), 0);
}
