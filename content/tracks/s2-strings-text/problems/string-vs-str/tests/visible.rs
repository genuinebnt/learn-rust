use solution::*;

#[test]
fn greets_literal_and_owned() {
    let name = String::from("Bo");
    check!(r#"greet("Ada") and greet(&String::from("Bo"))"#, (greet("Ada"), greet(&name)), ("Hello, Ada!".to_string(), "Hello, Bo!".to_string()));
}

#[test]
fn first() {
    check!(r#""hello world""#, first_word("hello world"), "hello");
}
