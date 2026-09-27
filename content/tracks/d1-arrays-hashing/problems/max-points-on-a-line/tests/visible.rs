use solution::*;

#[test]
fn diagonal() {
    check!(r#"points = [(1,1), (2,2), (3,3)]"#, max_points(&[(1, 1), (2, 2), (3, 3)]), 3);
}

#[test]
fn mixed() {
    check!(r#"points = [(1,1), (3,2), (5,3), (4,1), (2,3), (1,4)]"#, max_points(&[(1, 1), (3, 2), (5, 3), (4, 1), (2, 3), (1, 4)]), 4);
}

#[test]
fn single() {
    check!(r#"points = [(0,0)]"#, max_points(&[(0, 0)]), 1);
}
