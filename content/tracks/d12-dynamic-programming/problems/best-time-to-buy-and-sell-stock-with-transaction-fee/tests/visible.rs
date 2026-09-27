use solution::*;

#[test]
fn leetcode_fee_two() {
    check!(r#"prices = [1, 3, 2, 8, 4, 9], fee = 2"#, max_profit(&[1, 3, 2, 8, 4, 9], 2), 8);
}

#[test]
fn leetcode_fee_three() {
    check!(r#"prices = [1, 3, 7, 5, 10, 3], fee = 3"#, max_profit(&[1, 3, 7, 5, 10, 3], 3), 6);
}

#[test]
fn empty() {
    check!(r#"prices = [], fee = 1"#, max_profit(&[], 1), 0);
}

#[test]
fn one_day() {
    check!(r#"prices = [5], fee = 1"#, max_profit(&[5], 1), 0);
}

#[test]
fn fee_eats_the_gain() {
    check!(r#"prices = [1, 3], fee = 5"#, max_profit(&[1, 3], 5), 0);
}

#[test]
fn no_fee() {
    check!(r#"prices = [1, 3, 2, 4], fee = 0"#, max_profit(&[1, 3, 2, 4], 0), 4);
}
