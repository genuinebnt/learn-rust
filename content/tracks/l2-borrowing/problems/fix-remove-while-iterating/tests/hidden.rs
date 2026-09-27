use solution::*;

#[test]
fn adjacent() {
    check!(r#"["x1", "x2", "y"], prefix "x""#, { let mut v: Vec<String> = ["x1", "x2", "y"].map(String::from).to_vec(); remove_prefixed(&mut v, "x"); v }, vec!["y".to_string()]);
}
