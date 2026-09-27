use solution::*;
use std::cell::RefCell;
use std::rc::Rc;

#[test]
fn leetcode_seven() {
    check!(r#"root = [3, 2, 3, null, 3, null, 1]"#, rob(tree(&[Some(3), Some(2), Some(3), None, Some(3), None, Some(1)])), 7);
}

#[test]
fn leetcode_nine() {
    check!(r#"root = [3, 4, 5, 1, 3, null, 1]"#, rob(tree(&[Some(3), Some(4), Some(5), Some(1), Some(3), None, Some(1)])), 9);
}

#[test]
fn empty() {
    check!(r#"root = []"#, rob(tree(&[])), 0);
}

#[test]
fn one_house() {
    check!(r#"root = [5]"#, rob(tree(&[Some(5)])), 5);
}

#[test]
fn skip_two_levels() {
    check!(r#"root = [4, 1, null, 2, null, 3]"#, rob(tree(&[Some(4), Some(1), None, Some(2), None, Some(3)])), 7);
}

#[test]
fn built_by_hand() {
    let mut root = TreeNode::new(2);
    root.right = Some(Rc::new(RefCell::new(TreeNode::new(9))));
    let root = Rc::new(RefCell::new(root));
    check!(r#"root = [2, null, 9], built with TreeNode::new"#, rob(Some(root)), 9);
}
