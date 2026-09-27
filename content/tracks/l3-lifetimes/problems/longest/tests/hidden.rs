use solution::*;

#[test]
fn longer_second() {
    check!(r#""abc", "abcd""#, longest("abc", "abcd"), "abcd");
}

#[test]
fn owned_inputs() {
    let a = String::from("xy");
    let b = String::from("xyz!");
    check!(r#"two Strings"#, longest(&a, &b), "xyz!");
}
