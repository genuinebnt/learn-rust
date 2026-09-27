use solution::*;

#[test]
fn leetcode_five() {
    check!(r#"prices = [1, 2, 3, 0, 2]"#, max_profit(&[1, 2, 3, 0, 2]), 3);
}

#[test]
fn leetcode_one() {
    check!(r#"prices = [1]"#, max_profit(&[1]), 0);
}

#[test]
fn empty() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn falling() {
    check!(r#"prices = [5, 4, 3]"#, max_profit(&[5, 4, 3]), 0);
}

#[test]
fn cooldown_costs_a_trade() {
    check!(r#"prices = [1, 2, 1, 2]"#, max_profit(&[1, 2, 1, 2]), 1);
}
