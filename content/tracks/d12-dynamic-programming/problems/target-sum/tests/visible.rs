use solution::*;

#[test]
fn leetcode_five_ones() {
    check!(r#"nums = [1, 1, 1, 1, 1], target = 3"#, find_target_sum_ways(&[1, 1, 1, 1, 1], 3), 5);
}

#[test]
fn leetcode_single() {
    check!(r#"nums = [1], target = 1"#, find_target_sum_ways(&[1], 1), 1);
}

#[test]
fn empty_makes_zero() {
    check!(r#"nums = [], target = 0"#, find_target_sum_ways(&[], 0), 1);
}

#[test]
fn empty_cannot_make_one() {
    check!(r#"nums = [], target = 1"#, find_target_sum_ways(&[], 1), 0);
}

#[test]
fn zeros_take_both_signs() {
    check!(r#"nums = [0, 0], target = 0"#, find_target_sum_ways(&[0, 0], 0), 4);
}

#[test]
fn negative_target() {
    check!(r#"nums = [1], target = -1"#, find_target_sum_ways(&[1], -1), 1);
}
