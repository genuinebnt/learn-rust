use solution::*;

#[test]
fn two_zeros() {
    check!(r#"nums = [0, 4, 0]"#, product_except_self(&[0, 4, 0]), vec![0, 0, 0]);
}

#[test]
fn pair() {
    check!(r#"nums = [3, 5]"#, product_except_self(&[3, 5]), vec![5, 3]);
}
