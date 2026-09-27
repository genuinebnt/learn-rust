use solution::*;

#[test]
fn leetcode_two_trades() {
    check!(r#"prices = [7, 1, 5, 3, 6, 4]"#, max_profit(&[7, 1, 5, 3, 6, 4]), 7);
}

#[test]
fn leetcode_rising() {
    check!(r#"prices = [1, 2, 3, 4, 5]"#, max_profit(&[1, 2, 3, 4, 5]), 4);
}

#[test]
fn leetcode_falling() {
    check!(r#"prices = [7, 6, 4, 3, 1]"#, max_profit(&[7, 6, 4, 3, 1]), 0);
}

#[test]
fn no_days() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn one_day() {
    check!(r#"prices = [5]"#, max_profit(&[5]), 0);
}

#[test]
fn trade_every_rise() {
    check!(r#"prices = [1, 5, 1, 5]"#, max_profit(&[1, 5, 1, 5]), 8);
}
