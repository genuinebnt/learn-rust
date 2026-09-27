use solution::*;

#[test]
fn example() {
    check!(r#"[2,1,5,6,2,3]"#, largest_rectangle(&[2, 1, 5, 6, 2, 3]), 10);
}

#[test]
fn two() {
    check!(r#"[2,4]"#, largest_rectangle(&[2, 4]), 4);
}

#[test]
fn empty() {
    check!(r#"[]"#, largest_rectangle(&[]), 0);
}

#[test]
fn flat() {
    check!(r#"[3,3,3]"#, largest_rectangle(&[3, 3, 3]), 9);
}

#[test]
fn valley() {
    check!(r#"[5,0,5]"#, largest_rectangle(&[5, 0, 5]), 5);
}
