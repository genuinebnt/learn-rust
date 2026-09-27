use solution::*;

#[test]
fn leetcode_eleven() {
    check!(r#"max_choosable = 10, desired_total = 11"#, can_i_win(10, 11), false);
}

#[test]
fn leetcode_zero() {
    check!(r#"max_choosable = 10, desired_total = 0"#, can_i_win(10, 0), true);
}

#[test]
fn leetcode_one() {
    check!(r#"max_choosable = 10, desired_total = 1"#, can_i_win(10, 1), true);
}

#[test]
fn nobody_reaches_it() {
    check!(r#"max_choosable = 5, desired_total = 50"#, can_i_win(5, 50), false);
}

#[test]
fn must_think_ahead() {
    check!(r#"max_choosable = 4, desired_total = 6"#, can_i_win(4, 6), true);
}
