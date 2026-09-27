use solution::*;

#[test]
fn sum() {
    check!(r#"v = [1, 2, 3]"#, push_sum(vec![1, 2, 3]), vec![1, 2, 3, 6]);
}

#[test]
fn swap() {
    check!(r#"a = "x", b = "y""#, swap_owned("x".into(), "y".into()), ("y".to_string(), "x".to_string()));
}
