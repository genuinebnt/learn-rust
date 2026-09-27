use solution::*;

#[test]
fn single() {
    check!(r#"n = 1, edges = []"#, valid_tree(1, &[]), true);
}

#[test]
fn forest() {
    check!(r#"n = 4, edges = [(0,1), (2,3)]"#, valid_tree(4, &[(0, 1), (2, 3)]), false);
}

#[test]
fn right_count_but_cycle() {
    check!(r#"n = 4, edges = [(0,1), (1,0), (2,3)]"#, valid_tree(4, &[(0, 1), (1, 0), (2, 3)]), false);
}
