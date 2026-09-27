use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"root = [4,2,7,1,3,6,9]"#, level_order_values(&invert_tree(tree(&[Some(4), Some(2), Some(7), Some(1), Some(3), Some(6), Some(9)]))), vec![Some(4), Some(7), Some(2), Some(9), Some(6), Some(3), Some(1)]);
}

#[test]
fn leetcode_three() {
    check!(r#"root = [2,1,3]"#, level_order_values(&invert_tree(tree(&[Some(2), Some(1), Some(3)]))), vec![Some(2), Some(3), Some(1)]);
}

#[test]
fn empty() {
    check!(r#"root = []"#, invert_tree(None), None);
}

#[test]
fn single() {
    check!(r#"root = [1]"#, level_order_values(&invert_tree(tree(&[Some(1)]))), vec![Some(1)]);
}

#[test]
fn left_child_moves_right() {
    check!(r#"root = [1,2]"#, level_order_values(&invert_tree(tree(&[Some(1), Some(2)]))), vec![Some(1), None, Some(2)]);
}
