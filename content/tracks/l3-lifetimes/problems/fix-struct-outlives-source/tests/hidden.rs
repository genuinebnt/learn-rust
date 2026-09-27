use solution::*;

#[test]
fn none() {
    check!(r#"[]"#, first_lines(&[]).len(), 0);
}
