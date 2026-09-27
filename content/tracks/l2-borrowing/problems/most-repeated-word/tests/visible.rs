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
