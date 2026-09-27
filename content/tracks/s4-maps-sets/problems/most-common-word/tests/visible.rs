use solution::*;

#[test]
fn ball() {
    check!(r#""Bob hit a ball, the hit BALL flew far after it was hit.", banned = ["hit"]"#, most_common_word("Bob hit a ball, the hit BALL flew far after it was hit.", &["hit"]), "ball");
}

#[test]
fn single() {
    check!(r#""a.", banned = []"#, most_common_word("a.", &[]), "a");
}

#[test]
fn tie_alphabetical() {
    check!(r#""b a b a", banned = []"#, most_common_word("b a b a", &[]), "a");
}

#[test]
fn all_banned() {
    check!(r#""x y", banned = ["x", "y"]"#, most_common_word("x y", &["x", "y"]), "");
}

#[test]
fn case_insensitive() {
    check!(r#""Hello hello HELLO world", banned = []"#, most_common_word("Hello hello HELLO world", &[]), "hello");
}
