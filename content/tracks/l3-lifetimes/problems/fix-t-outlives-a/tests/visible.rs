use solution::*;

#[test]
fn pin_owned_and_borrowed() {
    let local = String::from("local");
    let mut b = Board::new();
    b.pin(1);
    b.pin(String::from("owned"));
    b.pin(local.as_str());
    check!(r#"pin 1, a String and a &str into a local String"#, b.render(), "<1> <owned> <local>");
}

#[test]
fn pin_all_borrows() {
    let items = vec![2, 3];
    let mut b = Board::new();
    pin_all(&mut b, &items);
    check!(r#"pin_all([2, 3])"#, b.render(), "<2> <3>");
}

#[test]
fn boxed_borrowed() {
    let local = String::from("x");
    check!(r#"boxed(&local)"#, boxed(&local).describe(), "<x>");
}

#[test]
fn boxed_forever_owned() {
    let v: Vec<Box<dyn Describe + 'static>> = vec![boxed_forever(String::from("kept"))];
    check!(r#"boxed_forever(String), kept in a 'static Vec"#, v[0].describe(), "<kept>");
}

#[test]
fn describe_each_example() {
    check!(r#"describe_each(["a", "b"])"#, describe_each(&["a", "b"]).collect::<Vec<_>>(), vec!["<a>".to_string(), "<b>".to_string()]);
}

#[test]
fn empty_board() {
    check!(r#"new board"#, Board::new().render(), "");
}
