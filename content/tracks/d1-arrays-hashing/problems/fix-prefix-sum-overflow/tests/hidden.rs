use solution::*;

#[test]
fn many_large() {
    check!(r#"nums = [2_000_000_000; 4]"#, max_prefix_sum(&[2_000_000_000; 4]), Some(8_000_000_000));
}

#[test]
fn all_negative() {
    check!(r#"nums = [-5, -1]"#, max_prefix_sum(&[-5, -1]), Some(-5));
}
