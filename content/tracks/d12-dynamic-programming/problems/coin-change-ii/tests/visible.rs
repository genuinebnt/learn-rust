use solution::*;

#[test]
fn leetcode_five() {
    check!(r#"amount = 5, coins = [1, 2, 5]"#, change(5, &[1, 2, 5]), 4);
}

#[test]
fn leetcode_impossible() {
    check!(r#"amount = 3, coins = [2]"#, change(3, &[2]), 0);
}

#[test]
fn leetcode_exact() {
    check!(r#"amount = 10, coins = [10]"#, change(10, &[10]), 1);
}

#[test]
fn zero_amount() {
    check!(r#"amount = 0, coins = [7]"#, change(0, &[7]), 1);
}

#[test]
fn order_does_not_matter() {
    check!(r#"amount = 4, coins = [1, 2] (1+1+2 and 2+1+1 are one combination)"#, change(4, &[1, 2]), 3);
}
