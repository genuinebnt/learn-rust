use solution::*;

#[test]
fn from_literals() {
    check!(r#"new("rust", ["rs"], Some("systems"))"#, Tag::new("rust", &["rs"], Some("systems")), Tag { name: "rust".to_string(), aliases: vec!["rs".to_string()], note: Some("systems".to_string()) });
}

#[test]
fn owned_name_is_moved() {
    let name = String::from("go");
    let ptr = name.as_ptr();
    let tag = Tag::new(name, &[], None);
    check!(r#"new(String "go", [], None): the tag keeps the caller's buffer"#, (tag.name.as_ptr() == ptr, tag.name), (true, "go".to_string()));
}

#[test]
fn borrowed_string() {
    let s = String::from("zig");
    check!(r#"new(&String "zig", ...), then use the String again"#, (Tag::new(&s, &[], None).name, s), ("zig".to_string(), "zig".to_string()));
}

#[test]
fn no_note() {
    check!(r#"new("c", ["clang", "c99"], None)"#, Tag::new("c", &["clang", "c99"], None), Tag { name: "c".to_string(), aliases: vec!["clang".to_string(), "c99".to_string()], note: None });
}

#[test]
fn outlives_its_inputs() {
    let tag = {
        let (n, a, note) = (String::from("tmp"), String::from("t"), String::from("n"));
        Tag::new(n.as_str(), &[a.as_str()], Some(note.as_str()))
    };
    check!(r#"tag built inside a block from local Strings"#, tag, Tag { name: "tmp".to_string(), aliases: vec!["t".to_string()], note: Some("n".to_string()) });
}
