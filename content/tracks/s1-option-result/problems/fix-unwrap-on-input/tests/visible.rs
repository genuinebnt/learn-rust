use solution::*;

#[test]
fn three() {
    check!(r#""1, 2, 3""#, average("1, 2, 3"), Ok(2.0));
}

#[test]
fn bad_item() {
    check!(r#""1, x""#, average("1, x"), Err("not a number: x".to_string()));
}

#[test]
fn blank() {
    check!(r#""""#, average(""), Err("no numbers".to_string()));
}

#[test]
fn single() {
    check!(r#""5""#, average("5"), Ok(5.0));
}

#[test]
fn empty_item_is_not_a_number() {
    check!(r#""1,,2""#, average("1,,2"), Err("not a number: ".to_string()));
}
