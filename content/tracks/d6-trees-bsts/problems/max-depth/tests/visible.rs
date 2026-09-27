use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"root = [3,9,20,null,null,15,7]"#, max_depth(tree(&[Some(3), Some(9), Some(20), None, None, Some(15), Some(7)])), 3);
}

#[test]
fn leetcode_right_child() {
    check!(r#"root = [1,null,2]"#, max_depth(tree(&[Some(1), None, Some(2)])), 2);
}

#[test]
fn empty() {
    check!(r#"root = []"#, max_depth(None), 0);
}

#[test]
fn single() {
    check!(r#"root = [1]"#, max_depth(tree(&[Some(1)])), 1);
}

#[test]
fn deepest_leaf_on_the_right() {
    check!(r#"root = [1,2,3,null,null,4,null,null,5]"#, max_depth(tree(&[Some(1), Some(2), Some(3), None, None, Some(4), None, None, Some(5)])), 4);
}
