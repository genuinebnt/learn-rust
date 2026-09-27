use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"root = [5,4,8,11,null,13,4,7,2,null,null,null,1], target_sum = 22"#, has_path_sum(tree(&[Some(5), Some(4), Some(8), Some(11), None, Some(13), Some(4), Some(7), Some(2), None, None, None, Some(1)]), 22), true);
}

#[test]
fn leetcode_no_path() {
    check!(r#"root = [1,2,3], target_sum = 5"#, has_path_sum(tree(&[Some(1), Some(2), Some(3)]), 5), false);
}

#[test]
fn empty_has_no_path() {
    check!(r#"root = [], target_sum = 0"#, has_path_sum(None, 0), false);
}

#[test]
fn must_end_at_a_leaf() {
    check!(r#"root = [1,2], target_sum = 1"#, has_path_sum(tree(&[Some(1), Some(2)]), 1), false);
}

#[test]
fn negatives() {
    check!(r#"root = [-2,null,-3], target_sum = -5"#, has_path_sum(tree(&[Some(-2), None, Some(-3)]), -5), true);
}
