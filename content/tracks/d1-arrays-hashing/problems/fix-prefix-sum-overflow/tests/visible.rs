use solution::*;

#[test]
fn small() {
    check!(r#"nums = [1, -2, 3]"#, max_prefix_sum(&[1, -2, 3]), Some(2));
}

#[test]
fn empty() {
    check!(r#"nums = []"#, max_prefix_sum(&[]), None);
}

#[test]
fn past_i32_max() {
    check!(r#"nums = [i32::MAX, 1]"#, max_prefix_sum(&[i32::MAX, 1]), Some(2_147_483_648));
}

#[test]
fn all_negative() {
    check!(r#"nums = [-5, -1]"#, max_prefix_sum(&[-5, -1]), Some(-5));
}

#[test]
fn peak_in_middle() {
    check!(r#"nums = [1, 2, -10, 4]"#, max_prefix_sum(&[1, 2, -10, 4]), Some(3));
}
