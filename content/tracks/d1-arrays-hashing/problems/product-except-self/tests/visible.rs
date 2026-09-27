use solution::*;

#[test]
fn four() {
    check!(r#"nums = [1, 2, 3, 4]"#, product_except_self(&[1, 2, 3, 4]), vec![24, 12, 8, 6]);
}

#[test]
fn with_zero() {
    check!(r#"nums = [-1, 1, 0, -3, 3]"#, product_except_self(&[-1, 1, 0, -3, 3]), vec![0, 0, 9, 0, 0]);
}

#[test]
fn pair() {
    check!(r#"nums = [2, 3]"#, product_except_self(&[2, 3]), vec![3, 2]);
}
