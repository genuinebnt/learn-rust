use solution::*;

#[test]
fn classic() {
    check!(r#"nums = [1, 0, -1, 0, -2, 2], target = 0"#, four_sum(&[1, 0, -1, 0, -2, 2], 0), vec![[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]);
}

#[test]
fn all_twos() {
    check!(r#"nums = [2, 2, 2, 2, 2], target = 8"#, four_sum(&[2, 2, 2, 2, 2], 8), vec![[2, 2, 2, 2]]);
}
