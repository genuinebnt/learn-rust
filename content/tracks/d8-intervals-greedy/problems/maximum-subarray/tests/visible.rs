use solution::*;

#[test]
fn leetcode_mixed() {
    check!(r#"nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]"#, max_subarray(&[-2, 1, -3, 4, -1, 2, 1, -5, 4]), Some(6));
}

#[test]
fn leetcode_single() {
    check!(r#"nums = [1]"#, max_subarray(&[1]), Some(1));
}

#[test]
fn leetcode_whole() {
    check!(r#"nums = [5, 4, -1, 7, 8]"#, max_subarray(&[5, 4, -1, 7, 8]), Some(23));
}

#[test]
fn empty() {
    check!(r#"nums = []"#, max_subarray(&[]), None);
}

#[test]
fn all_negative() {
    check!(r#"nums = [-3, -1, -2]"#, max_subarray(&[-3, -1, -2]), Some(-1));
}

#[test]
fn wider_than_i32() {
    check!(r#"nums = [2147483647, 2147483647]"#, max_subarray(&[i32::MAX, i32::MAX]), Some(4_294_967_294));
}
