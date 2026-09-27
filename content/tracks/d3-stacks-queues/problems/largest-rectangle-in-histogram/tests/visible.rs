use solution::*;

#[test]
fn example() {
    check!(r#"[2,1,5,6,2,3]"#, largest_rectangle(&[2, 1, 5, 6, 2, 3]), 10);
}

#[test]
fn two() {
    check!(r#"[2,4]"#, largest_rectangle(&[2, 4]), 4);
}
