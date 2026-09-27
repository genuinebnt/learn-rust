use solution::*;

#[test]
fn leetcode_two() {
    check!(r#"points = [(10, 16), (2, 8), (1, 6), (7, 12)]"#, find_min_arrow_shots(&[(10, 16), (2, 8), (1, 6), (7, 12)]), 2);
}

#[test]
fn leetcode_apart() {
    check!(r#"points = [(1, 2), (3, 4), (5, 6), (7, 8)]"#, find_min_arrow_shots(&[(1, 2), (3, 4), (5, 6), (7, 8)]), 4);
}

#[test]
fn leetcode_touching() {
    check!(r#"points = [(1, 2), (2, 3), (3, 4), (4, 5)]"#, find_min_arrow_shots(&[(1, 2), (2, 3), (3, 4), (4, 5)]), 2);
}

#[test]
fn no_balloons() {
    check!(r#"points = []"#, find_min_arrow_shots(&[]), 0);
}

#[test]
fn one_balloon() {
    check!(r#"points = [(3, 7)]"#, find_min_arrow_shots(&[(3, 7)]), 1);
}

#[test]
fn nested() {
    check!(r#"points = [(1, 10), (3, 4)]"#, find_min_arrow_shots(&[(1, 10), (3, 4)]), 1);
}
