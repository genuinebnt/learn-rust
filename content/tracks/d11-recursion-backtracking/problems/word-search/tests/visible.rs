use solution::*;

#[test]
fn leetcode_abcced() {
    check!(r#"board = ["ABCE", "SFCS", "ADEE"], word = "ABCCED""#, exist(&["ABCE", "SFCS", "ADEE"], "ABCCED"), true);
}

#[test]
fn leetcode_see() {
    check!(r#"board = ["ABCE", "SFCS", "ADEE"], word = "SEE""#, exist(&["ABCE", "SFCS", "ADEE"], "SEE"), true);
}

#[test]
fn leetcode_cell_used_twice() {
    check!(r#"board = ["ABCE", "SFCS", "ADEE"], word = "ABCB" (the B would be used twice)"#, exist(&["ABCE", "SFCS", "ADEE"], "ABCB"), false);
}

#[test]
fn single_cell() {
    check!(r#"board = ["A"], word = "A""#, exist(&["A"], "A"), true);
}

#[test]
fn no_diagonal_steps() {
    check!(r#"board = ["AB", "CD"], word = "AD""#, exist(&["AB", "CD"], "AD"), false);
}
