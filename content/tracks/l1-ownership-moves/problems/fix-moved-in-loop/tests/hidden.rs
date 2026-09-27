use solution::*;

#[test]
fn empty_name() {
    check!(r#"name = """#, { let mut out = vec![]; greet_thrice(String::new(), &mut out); out[2].clone() }, "hello, ".to_string());
}
