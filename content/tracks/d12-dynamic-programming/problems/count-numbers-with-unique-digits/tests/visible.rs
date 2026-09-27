use solution::*;

#[test]
fn leetcode_two() {
    check!(r#"n = 2"#, count_numbers_with_unique_digits(2), 91);
}

#[test]
fn leetcode_zero() {
    check!(r#"n = 0"#, count_numbers_with_unique_digits(0), 1);
}

#[test]
fn one_digit() {
    check!(r#"n = 1"#, count_numbers_with_unique_digits(1), 10);
}

#[test]
fn three_digits() {
    check!(r#"n = 3"#, count_numbers_with_unique_digits(3), 739);
}

#[test]
fn stops_growing_after_ten() {
    check!(r#"n = 11"#, count_numbers_with_unique_digits(11), 8_877_691);
}
