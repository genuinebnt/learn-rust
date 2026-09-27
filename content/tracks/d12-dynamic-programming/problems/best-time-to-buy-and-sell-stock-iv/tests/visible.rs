use solution::*;

#[test]
fn leetcode_three_days() {
    check!(r#"k = 2, prices = [2, 4, 1]"#, max_profit(2, &[2, 4, 1]), 2);
}

#[test]
fn leetcode_six_days() {
    check!(r#"k = 2, prices = [3, 2, 6, 5, 0, 3]"#, max_profit(2, &[3, 2, 6, 5, 0, 3]), 7);
}

#[test]
fn no_trades_allowed() {
    check!(r#"k = 0, prices = [1, 5]"#, max_profit(0, &[1, 5]), 0);
}

#[test]
fn empty() {
    check!(r#"k = 1, prices = []"#, max_profit(1, &[]), 0);
}

#[test]
fn one_trade() {
    check!(r#"k = 1, prices = [1, 5, 2, 6, 3, 7]"#, max_profit(1, &[1, 5, 2, 6, 3, 7]), 6);
}

#[test]
fn k_larger_than_needed() {
    check!(r#"k = 100, prices = [1, 2, 1, 2, 1, 2]"#, max_profit(100, &[1, 2, 1, 2, 1, 2]), 3);
}
