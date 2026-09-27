use solution::*;

#[test]
fn fruit() {
    check!(r#"["pear", "fig", "apple", "kiwi"]"#, { let mut w: Vec<String> = ["pear", "fig", "apple", "kiwi"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["fig", "kiwi", "pear", "apple"]);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut w: Vec<String> = vec![]; by_len_then_alpha(&mut w); w }, Vec::<String>::new());
}
