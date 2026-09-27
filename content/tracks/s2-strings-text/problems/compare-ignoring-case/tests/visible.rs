use solution::*;

#[test]
fn command() {
    check!(r#""  QUIT \n", "quit""#, is_command("  QUIT \n", "quit"), true);
}

#[test]
fn count() {
    check!(r#""The cat saw the THE", "the""#, count_word("The cat saw the THE", "the"), 3);
}
