use solution::*;

#[test]
fn leetcode_twelve() {
    check!(r#"n = 12"#, num_squares(12), 3);
}

#[test]
fn leetcode_thirteen() {
    check!(r#"n = 13"#, num_squares(13), 2);
}

#[test]
fn one() {
    check!(r#"n = 1"#, num_squares(1), 1);
}

#[test]
fn already_square() {
    check!(r#"n = 16"#, num_squares(16), 1);
}

#[test]
fn needs_four() {
    check!(r#"n = 7"#, num_squares(7), 4);
}
