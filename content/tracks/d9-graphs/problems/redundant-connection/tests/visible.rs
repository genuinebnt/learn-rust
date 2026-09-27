use solution::*;

#[test]
fn triangle() {
    check!(r#"edges = [(1,2), (1,3), (2,3)]"#, find_redundant(&[(1, 2), (1, 3), (2, 3)]), Some((2, 3)));
}

#[test]
fn longer_cycle() {
    check!(r#"edges = [(1,2), (2,3), (3,4), (1,4), (1,5)]"#, find_redundant(&[(1, 2), (2, 3), (3, 4), (1, 4), (1, 5)]), Some((1, 4)));
}

#[test]
fn repeated_edge() {
    check!(r#"edges = [(1,2), (1,2)]"#, find_redundant(&[(1, 2), (1, 2)]), Some((1, 2)));
}

#[test]
fn answer_is_not_the_last_edge() {
    check!(r#"edges = [(1,2), (2,3), (3,1), (1,4)]"#, find_redundant(&[(1, 2), (2, 3), (3, 1), (1, 4)]), Some((3, 1)));
}

#[test]
fn pair_returned_as_given() {
    check!(r#"edges = [(3,1), (2,3), (1,2)]"#, find_redundant(&[(3, 1), (2, 3), (1, 2)]), Some((1, 2)));
}
