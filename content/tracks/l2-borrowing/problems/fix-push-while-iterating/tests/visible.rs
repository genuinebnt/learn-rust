use solution::*;

#[test]
fn expands() {
    check!(r#"["a*", "b"]"#, { let mut v: Vec<String> = ["a*", "b"].map(String::from).to_vec(); expand(&mut v); v }, vec!["a*", "b", "a*.1", "a*.2"]);
}

#[test]
fn two_starred() {
    check!(r#"["a*", "b*"]"#, { let mut v: Vec<String> = ["a*", "b*"].map(String::from).to_vec(); expand(&mut v); v.len() }, 6);
}
