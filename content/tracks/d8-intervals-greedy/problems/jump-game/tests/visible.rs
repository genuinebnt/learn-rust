use solution::*;

#[test]
fn leetcode_reachable() {
    check!(r#"nums = [2, 3, 1, 1, 4]"#, can_jump(&[2, 3, 1, 1, 4]), true);
}

#[test]
fn leetcode_stuck() {
    check!(r#"nums = [3, 2, 1, 0, 4]"#, can_jump(&[3, 2, 1, 0, 4]), false);
}

#[test]
fn already_there() {
    check!(r#"nums = [0]"#, can_jump(&[0]), true);
}

#[test]
fn stuck_at_start() {
    check!(r#"nums = [0, 1]"#, can_jump(&[0, 1]), false);
}

#[test]
fn jump_over_a_zero() {
    check!(r#"nums = [2, 0, 1]"#, can_jump(&[2, 0, 1]), true);
}

#[test]
fn shorter_jumps_allowed() {
    check!(r#"nums = [5, 0]"#, can_jump(&[5, 0]), true);
}
