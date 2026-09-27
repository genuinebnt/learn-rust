use solution::*;

#[test]
fn three() {
    check!(r#"nums = [1, 2, 1]"#, concat_twice(&[1, 2, 1]), vec![1, 2, 1, 1, 2, 1]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, concat_twice(&[]), Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, concat_twice(&[5]), vec![5, 5]);
}
