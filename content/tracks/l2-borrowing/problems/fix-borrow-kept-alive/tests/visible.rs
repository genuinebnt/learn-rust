use solution::*;

#[test]
fn two() {
    check!(r#"names = ["ann", "bo"]"#, { let mut v = vec!["ann".to_string(), "bo".to_string()]; shout_first(&mut v); v }, vec!["ANN!".to_string(), "bo!".to_string()]);
}

#[test]
fn mixed_case() {
    check!(r#"names = ["Rust", "go", "C"]"#, { let mut v = vec!["Rust".to_string(), "go".to_string(), "C".to_string()]; shout_first(&mut v); v }, vec!["RUST!".to_string(), "go!".to_string(), "C!".to_string()]);
}

#[test]
fn already_upper() {
    check!(r#"names = ["ABC", "d"]"#, { let mut v = vec!["ABC".to_string(), "d".to_string()]; shout_first(&mut v); v }, vec!["ABC!".to_string(), "d!".to_string()]);
}

#[test]
fn only_first_uppercased() {
    check!(r#"names = ["a", "b", "c"]"#, { let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; shout_first(&mut v); v }, vec!["A!".to_string(), "b!".to_string(), "c!".to_string()]);
}

#[test]
fn one() {
    check!(r#"names = ["x"]"#, { let mut v = vec!["x".to_string()]; shout_first(&mut v); v }, vec!["X!".to_string()]);
}
