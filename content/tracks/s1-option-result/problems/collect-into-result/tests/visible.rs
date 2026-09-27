use solution::*;

#[test]
fn all_good() {
    check!(r#"["1", "2", "3"]"#, parse_all(&["1", "2", "3"]), Ok(vec![1, 2, 3]));
}

#[test]
fn first_bad() {
    check!(r#"["1", "x", "y"]"#, parse_all(&["1", "x", "y"]), Err("bad number: x".to_string()));
}

#[test]
fn no_items() {
    check!(r#"[]"#, parse_all(&[]), Ok(vec![]));
}

#[test]
fn signs() {
    check!(r#"["-1", "+2"]"#, parse_all(&["-1", "+2"]), Ok(vec![-1, 2]));
}

#[test]
fn empty_item_is_bad() {
    check!(r#"["1", ""]"#, parse_all(&["1", ""]), Err("bad number: ".to_string()));
}
