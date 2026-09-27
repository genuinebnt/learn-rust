use solution::*;

#[test]
fn leetcode_four_rows() {
    check!(r#"matrix = ["10100", "10111", "11111", "10010"]"#, maximal_square(&["10100", "10111", "11111", "10010"]), 4);
}

#[test]
fn leetcode_diagonal() {
    check!(r#"matrix = ["01", "10"]"#, maximal_square(&["01", "10"]), 1);
}

#[test]
fn leetcode_zero() {
    check!(r#"matrix = ["0"]"#, maximal_square(&["0"]), 0);
}

#[test]
fn empty() {
    check!(r#"matrix = []"#, maximal_square(&[]), 0);
}

#[test]
fn area_not_side() {
    check!(r#"matrix = ["111", "111", "111"]"#, maximal_square(&["111", "111", "111"]), 9);
}
