use solution::*;

#[test]
fn leetcode_three_by_seven() {
    check!(r#"m = 3, n = 7"#, unique_paths(3, 7), 28);
}

#[test]
fn leetcode_three_by_two() {
    check!(r#"m = 3, n = 2"#, unique_paths(3, 2), 3);
}

#[test]
fn one_cell() {
    check!(r#"m = 1, n = 1"#, unique_paths(1, 1), 1);
}

#[test]
fn one_row() {
    check!(r#"m = 1, n = 100"#, unique_paths(1, 100), 1);
}

#[test]
fn two_by_two() {
    check!(r#"m = 2, n = 2"#, unique_paths(2, 2), 2);
}
