use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"root = [3,9,20,null,null,15,7]"#, min_depth(tree(&[Some(3), Some(9), Some(20), None, None, Some(15), Some(7)])), 2);
}

#[test]
fn leetcode_right_path() {
    check!(r#"root = [2,null,3,null,4,null,5,null,6]"#, min_depth(tree(&[Some(2), None, Some(3), None, Some(4), None, Some(5), None, Some(6)])), 5);
}

#[test]
fn empty() {
    check!(r#"root = []"#, min_depth(None), 0);
}

#[test]
fn single() {
    check!(r#"root = [1]"#, min_depth(tree(&[Some(1)])), 1);
}

#[test]
fn one_child_is_not_a_leaf() {
    check!(r#"root = [1,2]"#, min_depth(tree(&[Some(1), Some(2)])), 2);
}
