use solution::*;

#[test]
fn classic() {
    check!(r#"nums = [-1, 2, 1, -4], target = 1"#, three_sum_closest(&[-1, 2, 1, -4], 1), 2);
}

#[test]
fn exact() {
    check!(r#"nums = [0, 0, 0], target = 1"#, three_sum_closest(&[0, 0, 0], 1), 0);
}

#[test]
fn below_zero_is_closer() {
    check!(r#"nums = [1, 1, 1], target = 0"#, three_sum_closest(&[1, 1, 1], 0), 3);
}

#[test]
fn exactly_three() {
    check!(r#"nums = [1, 2, 3], target = 100"#, three_sum_closest(&[1, 2, 3], 100), 6);
}

#[test]
fn negative_target() {
    check!(r#"nums = [-5, -4, -3, -2], target = -100"#, three_sum_closest(&[-5, -4, -3, -2], -100), -12);
}
