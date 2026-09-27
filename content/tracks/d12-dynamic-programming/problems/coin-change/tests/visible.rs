use solution::*;

#[test]
fn leetcode_eleven() {
    check!(r#"coins = [1, 2, 5], amount = 11"#, coin_change(&[1, 2, 5], 11), Some(3));
}

#[test]
fn leetcode_impossible() {
    check!(r#"coins = [2], amount = 3"#, coin_change(&[2], 3), None);
}

#[test]
fn leetcode_zero() {
    check!(r#"coins = [1], amount = 0"#, coin_change(&[1], 0), Some(0));
}

#[test]
fn greedy_fails() {
    check!(r#"coins = [1, 3, 4], amount = 6"#, coin_change(&[1, 3, 4], 6), Some(2));
}

#[test]
fn one_coin() {
    check!(r#"coins = [5], amount = 5"#, coin_change(&[5], 5), Some(1));
}

#[test]
fn no_coins() {
    check!(r#"coins = [], amount = 3"#, coin_change(&[], 3), None);
}
