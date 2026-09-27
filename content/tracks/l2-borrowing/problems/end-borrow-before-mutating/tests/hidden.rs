use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<String> = vec![]; append_longest(&mut v); v.len() }, 0);
}
