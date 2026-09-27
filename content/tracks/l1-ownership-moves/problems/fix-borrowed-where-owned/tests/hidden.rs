use solution::*;

#[test]
fn outlives_input() {
    check!(r#"tag kept after its input is dropped"#, { let t = { let s = String::from("tmp"); Tag::new(&s) }; t.name }, "tmp".to_string());
}
