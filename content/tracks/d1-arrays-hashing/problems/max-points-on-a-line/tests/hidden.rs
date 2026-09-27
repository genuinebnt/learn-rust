use solution::*;

#[test]
fn duplicates() {
    check!(r#"points = [(1,1), (1,1), (2,3)]"#, max_points(&[(1, 1), (1, 1), (2, 3)]), 3);
}

#[test]
fn vertical() {
    check!(r#"points = [(2,1), (2,5), (2,-3), (0,0)]"#, max_points(&[(2, 1), (2, 5), (2, -3), (0, 0)]), 3);
}

#[test]
fn empty() {
    check!(r#"points = []"#, max_points(&[]), 0);
}
