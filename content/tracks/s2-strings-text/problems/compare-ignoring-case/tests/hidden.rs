use solution::*;

#[test]
fn prefix_is_not_equal() {
    check!(r#""quitter", "quit""#, is_command("quitter", "quit"), false);
}

#[test]
fn none() {
    check!(r#""", "a""#, count_word("", "a"), 0);
}
