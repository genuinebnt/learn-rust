use solution::*;

#[test]
fn builds() {
    check!(r#"name = "rust""#, Tag::new("rust"), Tag { name: "rust".to_string() });
}

#[test]
fn from_string() {
    check!(r#"name from a String"#, { let s = String::from("go"); Tag::new(&s).name }, "go".to_string());
}

#[test]
fn empty() {
    check!(r#"name = """#, Tag::new(""), Tag { name: String::new() });
}

#[test]
fn with_spaces() {
    check!(r#"name = "big data""#, Tag::new("big data").name, "big data".to_string());
}

#[test]
fn exact_copy() {
    check!(r#"name = "Rust 2021""#, Tag::new("Rust 2021") == Tag { name: String::from("Rust 2021") }, true);
}
