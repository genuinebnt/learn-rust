use solution::*;

#[test]
fn leetcode_42() {
    check!(r#"s = "42""#, my_atoi("42"), 42);
}

#[test]
fn leetcode_spaces_sign_zero() {
    check!(r#"s = "   -042""#, my_atoi("   -042"), -42);
}

#[test]
fn leetcode_stops_at_letter() {
    check!(r#"s = "1337c0d3""#, my_atoi("1337c0d3"), 1337);
}

#[test]
fn leetcode_zero_then_minus() {
    check!(r#"s = "0-1""#, my_atoi("0-1"), 0);
}

#[test]
fn leetcode_words_first() {
    check!(r#"s = "words and 987""#, my_atoi("words and 987"), 0);
}

#[test]
fn clamps_below() {
    check!(r#"s = "-91283472332""#, my_atoi("-91283472332"), i32::MIN);
}

#[test]
fn empty() {
    check!(r#"s = """#, my_atoi(""), 0);
}
