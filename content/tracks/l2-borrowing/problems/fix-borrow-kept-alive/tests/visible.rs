use solution::*;

#[test]
fn two() {
    check!(r#"names = ["ann", "bo"]"#, { let mut v = vec!["ann".to_string(), "bo".to_string()]; shout_first(&mut v); v }, vec!["ANN!".to_string(), "bo!".to_string()]);
}

#[test]
fn mixed_case() {
    check!(r#"names = ["Rust", "go", "C"]"#, { let mut v = vec!["Rust".to_string(), "go".to_string(), "C".to_string()]; shout_first(&mut v); v }, vec!["RUST!".to_string(), "go!".to_string(), "C!".to_string()]);
}
