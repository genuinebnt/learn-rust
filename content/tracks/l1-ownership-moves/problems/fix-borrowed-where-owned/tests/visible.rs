use solution::*;

#[test]
fn builds() {
    check!(r#"name = "rust""#, Tag::new("rust"), Tag { name: "rust".to_string() });
}

#[test]
fn from_string() {
    check!(r#"name from a String"#, { let s = String::from("go"); Tag::new(&s).name }, "go".to_string());
}
