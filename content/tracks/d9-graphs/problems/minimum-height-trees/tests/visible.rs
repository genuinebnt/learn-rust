use solution::*;

#[test]
fn star_centre() {
    check!(r#"n = 4, edges = [(1, 0), (1, 2), (1, 3)]"#, find_min_height_trees(4, &[(1, 0), (1, 2), (1, 3)]), vec![1]);
}

#[test]
fn two_centres() {
    check!(r#"n = 6, edges = [(3, 0), (3, 1), (3, 2), (3, 4), (5, 4)]"#, find_min_height_trees(6, &[(3, 0), (3, 1), (3, 2), (3, 4), (5, 4)]), vec![3, 4]);
}

#[test]
fn one_node() {
    check!(r#"n = 1, edges = []"#, find_min_height_trees(1, &[]), vec![0]);
}

#[test]
fn two_nodes() {
    check!(r#"n = 2, edges = [(0, 1)]"#, find_min_height_trees(2, &[(0, 1)]), vec![0, 1]);
}

#[test]
fn path_of_five() {
    check!(r#"n = 5, path 0-1-2-3-4"#, find_min_height_trees(5, &[(0, 1), (1, 2), (2, 3), (3, 4)]), vec![2]);
}
