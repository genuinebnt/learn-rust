use solution::*;

#[test]
fn larger_exists() {
    check!(r#"v = [3, 9], x = 4"#, { let mut v = vec![3, 9]; (add_and_max(&mut v, 4), v) }, (9, vec![3, 9, 4]));
}

#[test]
fn x_is_max() {
    check!(r#"v = [1], x = 5"#, { let mut v = vec![1]; add_and_max(&mut v, 5) }, 5);
}

#[test]
fn negatives() {
    check!(r#"v = [-5, -9], x = -7"#, { let mut v = vec![-5, -9]; (add_and_max(&mut v, -7), v) }, (-5, vec![-5, -9, -7]));
}

#[test]
fn max_in_middle() {
    check!(r#"v = [1, 8, 2], x = 3"#, { let mut v = vec![1, 8, 2]; add_and_max(&mut v, 3) }, 8);
}

#[test]
fn x_equals_max() {
    check!(r#"v = [4, 2], x = 4"#, { let mut v = vec![4, 2]; (add_and_max(&mut v, 4), v) }, (4, vec![4, 2, 4]));
}
