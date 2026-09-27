use solution::*;

#[test]
fn triangle() {
    check!(r#"n = 3, edges = [(0, 1), (1, 2), (2, 0)], source = 0, destination = 2"#, valid_path(3, &[(0, 1), (1, 2), (2, 0)], 0, 2), true);
}

#[test]
fn separate_pieces() {
    check!(r#"n = 6, edges = [(0, 1), (0, 2), (3, 5), (5, 4), (4, 3)], source = 0, destination = 5"#, valid_path(6, &[(0, 1), (0, 2), (3, 5), (5, 4), (4, 3)], 0, 5), false);
}

#[test]
fn source_is_destination() {
    check!(r#"n = 1, edges = [], source = 0, destination = 0"#, valid_path(1, &[], 0, 0), true);
}

#[test]
fn edges_work_both_ways() {
    check!(r#"n = 2, edges = [(1, 0)], source = 0, destination = 1"#, valid_path(2, &[(1, 0)], 0, 1), true);
}

#[test]
fn isolated_destination() {
    check!(r#"n = 3, edges = [(0, 1)], source = 0, destination = 2"#, valid_path(3, &[(0, 1)], 0, 2), false);
}
