use solution::*;

#[test]
fn leetcode_hundred() {
    check!(r#"digits = [1, 3, 5, 7], n = 100"#, at_most_n_given_digit_set(&[1, 3, 5, 7], 100), 20);
}

#[test]
fn leetcode_billion() {
    check!(r#"digits = [1, 4, 9], n = 1000000000"#, at_most_n_given_digit_set(&[1, 4, 9], 1_000_000_000), 29523);
}

#[test]
fn leetcode_seven() {
    check!(r#"digits = [7], n = 8"#, at_most_n_given_digit_set(&[7], 8), 1);
}

#[test]
fn n_itself_counts() {
    check!(r#"digits = [1], n = 11"#, at_most_n_given_digit_set(&[1], 11), 2);
}

#[test]
fn no_digits() {
    check!(r#"digits = [], n = 100"#, at_most_n_given_digit_set(&[], 100), 0);
}
