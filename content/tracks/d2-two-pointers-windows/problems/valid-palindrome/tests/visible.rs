use solution::*;

#[test]
fn panama() {
    check!(r#"s = "A man, a plan, a canal: Panama""#, is_palindrome("A man, a plan, a canal: Panama"), true);
}

#[test]
fn race_a_car() {
    check!(r#"s = "race a car""#, is_palindrome("race a car"), false);
}

#[test]
fn only_punctuation() {
    check!(r#"s = " .,""#, is_palindrome(" .,"), true);
}

#[test]
fn single_space() {
    check!(r#"s = " ""#, is_palindrome(" "), true);
}

#[test]
fn empty() {
    check!(r#"s = """#, is_palindrome(""), true);
}

#[test]
fn case_ignored() {
    check!(r#"s = "No lemon, no melon""#, is_palindrome("No lemon, no melon"), true);
}
