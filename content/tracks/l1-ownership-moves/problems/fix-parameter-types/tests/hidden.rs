use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, { let mut w: Vec<String> = vec![]; shout_all(&mut w); into_sentence(w) }, String::new());
}
