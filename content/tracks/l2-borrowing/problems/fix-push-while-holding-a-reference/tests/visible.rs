use solution::*;

#[test]
fn larger_exists() {
    check!(r#"v = [3, 9], x = 4"#, { let mut v = vec![3, 9]; (add_and_max(&mut v, 4), v) }, (9, vec![3, 9, 4]));
}

#[test]
fn x_is_max() {
    check!(r#"v = [1], x = 5"#, { let mut v = vec![1]; add_and_max(&mut v, 5) }, 5);
}
