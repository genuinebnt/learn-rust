use solution::*;

#[test]
fn round_trip() {
    check!(r#"["lint", "code", "love", "you"]"#, decode(&encode(&["lint", "code", "love", "you"])), vec!["lint", "code", "love", "you"]);
}

#[test]
fn delimiters_inside() {
    check!(r##"["a#b", "12#", "#"]"##, decode(&encode(&["a#b", "12#", "#"])), vec!["a#b", "12#", "#"]);
}

#[test]
fn empty_strings() {
    check!(r#"["", ""]"#, decode(&encode(&["", ""])), vec!["", ""]);
}
