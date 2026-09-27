use solution::*;

#[test]
fn leetcode_eight() {
    check!(r#"prices = [3, 3, 5, 0, 0, 3, 1, 4]"#, max_profit(&[3, 3, 5, 0, 0, 3, 1, 4]), 6);
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
fn empty() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn one_day() {
    check!(r#"prices = [1]"#, max_profit(&[1]), 0);
}

#[test]
fn at_most_two() {
    check!(r#"prices = [1, 5, 2, 6, 3, 7] (three rises, only two trades)"#, max_profit(&[1, 5, 2, 6, 3, 7]), 9);
}
