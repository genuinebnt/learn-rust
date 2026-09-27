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
