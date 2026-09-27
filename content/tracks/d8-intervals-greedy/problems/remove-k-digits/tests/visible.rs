use solution::*;

#[test]
fn leetcode_1219() {
    check!(r#"num = "1432219", k = 3"#, remove_kdigits("1432219", 3), "1219");
}

#[test]
fn leetcode_leading_zero() {
    check!(r#"num = "10200", k = 1"#, remove_kdigits("10200", 1), "200");
}

#[test]
fn leetcode_nothing_left() {
    check!(r#"num = "10", k = 2"#, remove_kdigits("10", 2), "0");
}

#[test]
fn remove_none() {
    check!(r#"num = "123", k = 0"#, remove_kdigits("123", 0), "123");
}

#[test]
fn rising_drops_the_end() {
    check!(r#"num = "12345", k = 2"#, remove_kdigits("12345", 2), "123");
}

#[test]
fn single_digit_removed() {
    check!(r#"num = "9", k = 1"#, remove_kdigits("9", 1), "0");
}
