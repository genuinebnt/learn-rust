use solution::*;

#[test]
fn leetcode_twelve() {
    check!(r#"s = "12""#, num_decodings("12"), 2);
}

#[test]
fn leetcode_two_two_six() {
    check!(r#"s = "226""#, num_decodings("226"), 3);
}

#[test]
fn leetcode_leading_zero() {
    check!(r#"s = "06""#, num_decodings("06"), 0);
}

#[test]
fn single_zero() {
    check!(r#"s = "0""#, num_decodings("0"), 0);
}

#[test]
fn single_digit() {
    check!(r#"s = "1""#, num_decodings("1"), 1);
}

#[test]
fn ten_only_as_a_pair() {
    check!(r#"s = "10""#, num_decodings("10"), 1);
}

#[test]
fn above_twenty_six() {
    check!(r#"s = "27""#, num_decodings("27"), 1);
}
