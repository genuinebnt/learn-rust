use solution::*;

#[test]
fn classic() {
    check!(r#"nums = [-1, 2, 1, -4], target = 1"#, three_sum_closest(&[-1, 2, 1, -4], 1), 2);
}

#[test]
fn exact() {
    check!(r#"nums = [0, 0, 0], target = 1"#, three_sum_closest(&[0, 0, 0], 1), 0);
}
