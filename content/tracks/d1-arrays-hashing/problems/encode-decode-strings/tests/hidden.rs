use solution::*;

#[test]
fn no_words() {
    check!(r#"[]"#, decode(&encode(&[])), Vec::<String>::new());
}

#[test]
fn unicode() {
    check!(r#"["héllo", "🦀#rust"]"#, decode(&encode(&["héllo", "🦀#rust"])), vec!["héllo", "🦀#rust"]);
}
