use solution::*;

#[test]
fn example() {
    check!(r#"342 + 465"#, values(&add_two_numbers(list(&[2, 4, 3]), list(&[5, 6, 4]))), vec![7, 0, 8]);
}

#[test]
fn zeros() {
    check!(r#"0 + 0"#, values(&add_two_numbers(list(&[0]), list(&[0]))), vec![0]);
}
