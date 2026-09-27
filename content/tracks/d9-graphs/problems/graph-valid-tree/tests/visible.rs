use solution::*;

#[test]
fn tree() {
    check!(r#"n = 5, edges = [(0,1), (0,2), (0,3), (1,4)]"#, valid_tree(5, &[(0, 1), (0, 2), (0, 3), (1, 4)]), true);
}

#[test]
fn cycle() {
    check!(r#"n = 5, edges = [(0,1), (1,2), (2,3), (1,3), (1,4)]"#, valid_tree(5, &[(0, 1), (1, 2), (2, 3), (1, 3), (1, 4)]), false);
}
