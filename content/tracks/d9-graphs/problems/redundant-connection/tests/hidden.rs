use solution::*;

#[test]
fn reversed_pairs() {
    check!(r#"edges = [(2,1), (3,1), (4,2), (1,4)]"#, find_redundant(&[(2, 1), (3, 1), (4, 2), (1, 4)]), Some((1, 4)));
}

#[test]
fn double_edge() {
    check!(r#"edges = [(1,2), (2,1)]"#, find_redundant(&[(1, 2), (2, 1)]), Some((2, 1)));
}
