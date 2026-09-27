use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"nums = [3, 1, 5, 8]"#, max_coins(&[3, 1, 5, 8]), 167);
}

#[test]
fn leetcode_two() {
    check!(r#"nums = [1, 5]"#, max_coins(&[1, 5]), 10);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, max_coins(&[]), 0);
}

#[test]
fn one() {
    check!(r#"nums = [7]"#, max_coins(&[7]), 7);
}

#[test]
fn three() {
    check!(r#"nums = [2, 3, 4]"#, max_coins(&[2, 3, 4]), 36);
}
