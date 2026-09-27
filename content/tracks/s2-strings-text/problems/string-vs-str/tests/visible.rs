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

#[test]
fn exclaim_once() {
    let mut s = String::from("wow");
    exclaim(&mut s);
    check!(r#"exclaim on "wow""#, s, "wow!".to_string());
}

#[test]
fn first_whole_word() {
    check!(r#""rust""#, first_word("rust"), "rust");
}

#[test]
fn greet_empty() {
    check!(r#""""#, greet(""), "Hello, !".to_string());
}
