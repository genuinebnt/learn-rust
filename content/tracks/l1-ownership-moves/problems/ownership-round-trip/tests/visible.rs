use solution::*;

#[test]
fn sum() {
    check!(r#"v = [1, 2, 3]"#, push_sum(vec![1, 2, 3]), vec![1, 2, 3, 6]);
}

#[test]
fn swap() {
    check!(r#"a = "x", b = "y""#, swap_owned("x".into(), "y".into()), ("y".to_string(), "x".to_string()));
}

#[test]
fn swap_empty() {
    check!(r#"a = "", b = "z""#, swap_owned(String::new(), "z".into()), ("z".to_string(), String::new()));
}

#[test]
fn sum_of_one() {
    check!(r#"v = [4]"#, push_sum(vec![4]), vec![4, 4]);
}

#[test]
fn sum_negative() {
    check!(r#"v = [-1, -2]"#, push_sum(vec![-1, -2]), vec![-1, -2, -3]);
}
