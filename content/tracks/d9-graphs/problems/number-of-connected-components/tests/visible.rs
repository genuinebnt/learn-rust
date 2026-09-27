use solution::*;

#[test]
fn two() {
    check!(r#"n = 5, edges = [(0,1), (1,2), (3,4)]"#, count_components(5, &[(0, 1), (1, 2), (3, 4)]), 2);
}

#[test]
fn one() {
    check!(r#"n = 5, edges = [(0,1), (1,2), (2,3), (3,4)]"#, count_components(5, &[(0, 1), (1, 2), (2, 3), (3, 4)]), 1);
}

#[test]
fn single_node() {
    check!(r#"n = 1, edges = []"#, count_components(1, &[]), 1);
}

#[test]
fn no_edges() {
    check!(r#"n = 4, edges = []"#, count_components(4, &[]), 4);
}

#[test]
fn repeated_and_cyclic_edges() {
    check!(r#"n = 4, edges = [(0,1), (1,0), (1,2), (2,0)]"#, count_components(4, &[(0, 1), (1, 0), (1, 2), (2, 0)]), 2);
}
