use solution::*;

#[test]
fn hit() {
    check!(r#"nums = [1, 1, 1, 0], target = 3"#, three_sum_closest(&[1, 1, 1, 0], 3), 3);
}

#[test]
fn negative_target() {
    check!(r#"nums = [4, 0, 5, -5, 3, 3, 0, -4, -5], target = -2"#, three_sum_closest(&[4, 0, 5, -5, 3, 3, 0, -4, -5], -2), -2);
}
