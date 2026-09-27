use solution::*;

#[test]
fn fruit() {
    check!(r#"["pear", "fig", "apple", "kiwi"]"#, { let mut w: Vec<String> = ["pear", "fig", "apple", "kiwi"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["fig", "kiwi", "pear", "apple"]);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut w: Vec<String> = vec![]; by_len_then_alpha(&mut w); w }, Vec::<String>::new());
}

#[test]
fn ties_alphabetical() {
    check!(r#"["dd", "cc", "a"]"#, { let mut w: Vec<String> = ["dd", "cc", "a"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["a", "cc", "dd"]);
}

#[test]
fn duplicates() {
    check!(r#"["b", "a", "b"]"#, { let mut w: Vec<String> = ["b", "a", "b"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["a", "b", "b"]);
}

#[test]
fn shorter_first() {
    check!(r#"["abc", "z"]"#, { let mut w: Vec<String> = ["abc", "z"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["z", "abc"]);
}
