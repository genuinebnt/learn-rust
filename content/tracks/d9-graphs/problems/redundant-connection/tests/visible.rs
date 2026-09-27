use solution::*;

#[test]
fn triangle() {
    check!(r#"edges = [(1,2), (1,3), (2,3)]"#, find_redundant(&[(1, 2), (1, 3), (2, 3)]), Some((2, 3)));
}

#[test]
fn longer_cycle() {
    check!(r#"edges = [(1,2), (2,3), (3,4), (1,4), (1,5)]"#, find_redundant(&[(1, 2), (2, 3), (3, 4), (1, 4), (1, 5)]), Some((1, 4)));
}
