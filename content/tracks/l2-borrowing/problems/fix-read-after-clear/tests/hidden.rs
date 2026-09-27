use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<String> = vec![]; longest_then_clear(&mut v) }, 0);
}
