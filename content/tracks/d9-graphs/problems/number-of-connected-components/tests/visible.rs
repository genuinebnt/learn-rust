use solution::*;

#[test]
fn two() {
    check!(r#"n = 5, edges = [(0,1), (1,2), (3,4)]"#, count_components(5, &[(0, 1), (1, 2), (3, 4)]), 2);
}

#[test]
fn one() {
    check!(r#"n = 5, edges = [(0,1), (1,2), (2,3), (3,4)]"#, count_components(5, &[(0, 1), (1, 2), (2, 3), (3, 4)]), 1);
}
