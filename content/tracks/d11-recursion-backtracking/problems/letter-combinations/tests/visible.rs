use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_two_three() {
    check!(r#"digits = "23""#, sorted(letter_combinations("23")), vec!["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]);
}

#[test]
fn leetcode_empty() {
    check!(r#"digits = """#, letter_combinations(""), Vec::<String>::new());
}

#[test]
fn leetcode_single() {
    check!(r#"digits = "2""#, sorted(letter_combinations("2")), vec!["a", "b", "c"]);
}

#[test]
fn seven_has_four_letters() {
    check!(r#"digits = "7""#, sorted(letter_combinations("7")), vec!["p", "q", "r", "s"]);
}

#[test]
fn repeated_digit() {
    check!(r#"digits = "22""#, sorted(letter_combinations("22")), vec!["aa", "ab", "ac", "ba", "bb", "bc", "ca", "cb", "cc"]);
}
