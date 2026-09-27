use solution::*;

#[test]
fn ball() {
    check!(r#""Bob hit a ball, the hit BALL flew far after it was hit.", banned = ["hit"]"#, most_common_word("Bob hit a ball, the hit BALL flew far after it was hit.", &["hit"]), "ball");
}

#[test]
fn single() {
    check!(r#""a.", banned = []"#, most_common_word("a.", &[]), "a");
}
