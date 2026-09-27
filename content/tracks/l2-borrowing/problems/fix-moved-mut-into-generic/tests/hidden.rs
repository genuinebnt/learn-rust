use solution::*;

#[test]
fn empty() {
    check!(r#"s = """#, { let mut o = String::from("z"); write_twice(&mut o, ""); o }, "z".to_string());
}
