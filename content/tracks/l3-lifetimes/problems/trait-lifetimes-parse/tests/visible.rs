use solution::*;

#[test]
fn fields_of_pairs() {
    check!(r#"fields::<Pair>("a=1, b = 2")"#, fields::<Pair>("a=1, b = 2"), Some(vec![Pair { key: "a", value: "1" }, Pair { key: "b", value: "2" }]));
}

#[test]
fn fields_of_strs() {
    check!(r#"fields::<&str>(" x ,y")"#, fields::<&str>(" x ,y"), Some(vec!["x", "y"]));
}

#[test]
fn fields_of_numbers() {
    check!(r#"fields::<u32>("1, 2,3")"#, fields::<u32>("1, 2,3"), Some(vec![1, 2, 3]));
}

#[test]
fn read_owned_number() {
    check!(r#"read_owned::<u32>(" 42\n")"#, read_owned::<u32>(" 42\n".as_bytes()), Some(42));
}

#[test]
fn read_owned_string() {
    check!(r#"read_owned::<String>("hi \nnext")"#, read_owned::<String>("hi \nnext".as_bytes()), Some("hi".to_string()));
}

#[test]
fn pair_without_equals() {
    check!(r#"fields::<Pair>("a=1,b")"#, fields::<Pair>("a=1,b"), None);
}
