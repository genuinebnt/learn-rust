use solution::*;

#[test]
fn whitespace_only() {
    check!(r#""   ""#, average("   "), Err("no numbers".to_string()));
}

#[test]
fn trailing_comma() {
    check!(r#""4,""#, average("4,"), Err("not a number: ".to_string()));
}
