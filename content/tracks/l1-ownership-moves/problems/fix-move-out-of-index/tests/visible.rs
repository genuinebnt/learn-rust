use solution::*;

#[test]
fn takes() {
    check!(r#"names = ["ann", "bo"]"#, { let mut v = vec!["ann".to_string(), "bo".to_string()]; let f = take_first(&mut v); (f, v) }, ("ann".to_string(), vec![String::new(), "bo".to_string()]));
}

#[test]
fn single() {
    check!(r#"names = ["x"]"#, { let mut v = vec!["x".to_string()]; take_first(&mut v) }, "x".to_string());
}
