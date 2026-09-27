use solution::*;

#[test]
fn repeated() {
    let text = String::from("b a b c a b");
    check!(r#""b a b c a b""#, most_repeated(&text), Some("b"));
}

#[test]
fn empty() {
    check!(r#""""#, most_repeated(""), None);
}

#[test]
fn single_word() {
    check!(r#""hello""#, most_repeated("hello"), Some("hello"));
}

#[test]
fn tie_alphabetical() {
    check!(r#""x y y x""#, most_repeated("x y y x"), Some("x"));
}

#[test]
fn case_sensitive() {
    check!(r#""A a a A A""#, most_repeated("A a a A A"), Some("A"));
}
