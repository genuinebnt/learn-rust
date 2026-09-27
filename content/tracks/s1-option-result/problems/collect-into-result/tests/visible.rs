use solution::*;

#[test]
fn all_good() {
    check!(r#"["1", "2", "3"]"#, parse_all(&["1", "2", "3"]), Ok(vec![1, 2, 3]));
}

#[test]
fn first_bad() {
    check!(r#"["1", "x", "y"]"#, parse_all(&["1", "x", "y"]), Err("bad number: x".to_string()));
}
