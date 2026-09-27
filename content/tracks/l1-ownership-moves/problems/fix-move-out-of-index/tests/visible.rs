use solution::*;

#[test]
fn takes() {
    check!(r#"names = ["ann", "bo"]"#, { let mut v = vec!["ann".to_string(), "bo".to_string()]; let f = take_first(&mut v); (f, v) }, ("ann".to_string(), vec![String::new(), "bo".to_string()]));
}

#[test]
fn single() {
    check!(r#"names = ["x"]"#, { let mut v = vec!["x".to_string()]; take_first(&mut v) }, "x".to_string());
}

#[test]
fn leaves_empty_string() {
    check!(r#"names = ["x"]"#, { let mut v = vec!["x".to_string()]; take_first(&mut v); v }, vec![String::new()]);
}

#[test]
fn others_untouched() {
    check!(r#"names = ["a", "b"]"#, { let mut v = vec!["a".to_string(), "b".to_string()]; take_first(&mut v); v[1].clone() }, "b".to_string());
}

#[test]
fn second_call() {
    check!(r#"take_first twice on ["a"]"#, { let mut v = vec!["a".to_string()]; take_first(&mut v); take_first(&mut v) }, String::new());
}
