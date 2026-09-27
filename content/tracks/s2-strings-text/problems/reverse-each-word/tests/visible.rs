use solution::*;

#[test]
fn accents() {
    check!(r#""héllo wörld""#, reverse_each_word("héllo wörld"), "olléh dlröw".to_string());
}

#[test]
fn ascii() {
    check!(r#""ab cd""#, reverse_each_word("ab cd"), "ba dc".to_string());
}
