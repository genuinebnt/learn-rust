use solution::*;

#[test]
fn command() {
    check!(r#""  QUIT \n", "quit""#, is_command("  QUIT \n", "quit"), true);
}

#[test]
fn count() {
    check!(r#""The cat saw the THE", "the""#, count_word("The cat saw the THE", "the"), 3);
}

#[test]
fn different_word() {
    check!(r#""help", "quit""#, is_command("help", "quit"), false);
}

#[test]
fn whole_words_only() {
    check!(r#""cats cat category", "CAT""#, count_word("cats cat category", "CAT"), 1);
}

#[test]
fn any_whitespace() {
    check!(r#""a\nA\ta", "a""#, count_word("a\nA\ta", "a"), 3);
}
