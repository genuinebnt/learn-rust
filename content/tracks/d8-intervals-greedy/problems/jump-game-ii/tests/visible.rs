use solution::*;

#[test]
fn leetcode_two() {
    check!(r#"nums = [2, 3, 1, 1, 4]"#, jump(&[2, 3, 1, 1, 4]), Some(2));
}

#[test]
fn leetcode_zero_inside() {
    check!(r#"nums = [2, 3, 0, 1, 4]"#, jump(&[2, 3, 0, 1, 4]), Some(2));
}

#[test]
fn already_there() {
    check!(r#"nums = [0]"#, jump(&[0]), Some(0));
}

#[test]
fn unreachable() {
    check!(r#"nums = [1, 0, 1]"#, jump(&[1, 0, 1]), None);
}

#[test]
fn one_step_at_a_time() {
    check!(r#"nums = [1, 1, 1, 1]"#, jump(&[1, 1, 1, 1]), Some(3));
}

#[test]
fn longest_jump_is_not_best() {
    check!(r#"nums = [3, 1, 4, 1, 1, 1, 1]"#, jump(&[3, 1, 4, 1, 1, 1, 1]), Some(2));
}
