use solution::*;

#[test]
fn four_numbers() {
    check!(r#"nums = [1, 2, 3, 4]"#, running_sum(&[1, 2, 3, 4]), vec![1, 3, 6, 10]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, running_sum(&[]), Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, running_sum(&[5]), vec![5]);
}
