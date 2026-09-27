use solution::*;

#[test]
fn tree() {
    check!(r#"n = 5, edges = [(0,1), (0,2), (0,3), (1,4)]"#, valid_tree(5, &[(0, 1), (0, 2), (0, 3), (1, 4)]), true);
}

#[test]
fn cycle() {
    check!(r#"n = 5, edges = [(0,1), (1,2), (2,3), (1,3), (1,4)]"#, valid_tree(5, &[(0, 1), (1, 2), (2, 3), (1, 3), (1, 4)]), false);
}

#[test]
fn single_edge() {
    check!(r#"n = 2, edges = [(0,1)]"#, valid_tree(2, &[(0, 1)]), true);
}

#[test]
fn not_connected() {
    check!(r#"n = 2, edges = []"#, valid_tree(2, &[]), false);
}

#[test]
fn triangle() {
    check!(r#"n = 3, edges = [(0,1), (1,2), (2,0)]"#, valid_tree(3, &[(0, 1), (1, 2), (2, 0)]), false);
}
