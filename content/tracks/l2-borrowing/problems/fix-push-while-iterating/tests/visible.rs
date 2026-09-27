use solution::*;

#[test]
fn expands() {
    check!(r#"["a*", "b"]"#, { let mut v: Vec<String> = ["a*", "b"].map(String::from).to_vec(); expand(&mut v); v }, vec!["a*", "b", "a*.1", "a*.2"]);
}

#[test]
fn two_starred() {
    check!(r#"["a*", "b*"]"#, { let mut v: Vec<String> = ["a*", "b*"].map(String::from).to_vec(); expand(&mut v); v.len() }, 6);
}

#[test]
fn star_in_middle() {
    check!(r#"["a*b"]"#, { let mut v = vec!["a*b".to_string()]; expand(&mut v); v }, vec!["a*b"]);
}

#[test]
fn order() {
    check!(r#"["b*", "x", "a*"]"#, { let mut v: Vec<String> = ["b*", "x", "a*"].map(String::from).to_vec(); expand(&mut v); v }, vec!["b*", "x", "a*", "b*.1", "b*.2", "a*.1", "a*.2"]);
}

#[test]
fn none() {
    check!(r#"["x"]"#, { let mut v = vec!["x".to_string()]; expand(&mut v); v.len() }, 1);
}
