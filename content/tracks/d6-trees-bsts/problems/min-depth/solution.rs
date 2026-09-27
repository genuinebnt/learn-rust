use std::cell::RefCell;
use std::collections::VecDeque;
use std::rc::Rc;

#[derive(Debug, PartialEq, Eq)]
pub struct TreeNode {
    pub val: i32,
    pub left: Option<Rc<RefCell<TreeNode>>>,
    pub right: Option<Rc<RefCell<TreeNode>>>,
}

impl TreeNode {
    pub fn new(val: i32) -> Self {
        TreeNode { val, left: None, right: None }
    }
}

/// Builds a tree from LeetCode's level-order form: `None` is a missing child.
pub fn tree(values: &[Option<i32>]) -> Option<Rc<RefCell<TreeNode>>> {
    let mut it = values.iter();
    let root = Rc::new(RefCell::new(TreeNode::new((*it.next()?)?)));
    let mut queue = VecDeque::from([root.clone()]);
    while let Some(node) = queue.pop_front() {
        let n = &mut *node.borrow_mut();
        for child in [&mut n.left, &mut n.right] {
            match it.next() {
                None => return Some(root),
                Some(&Some(val)) => {
                    let c = Rc::new(RefCell::new(TreeNode::new(val)));
                    queue.push_back(c.clone());
                    *child = Some(c);
                }
                Some(None) => {}
            }
        }
    }
    Some(root)
}

/// The tree in LeetCode's level-order form, with trailing `None`s trimmed.
pub fn level_order_values(root: &Option<Rc<RefCell<TreeNode>>>) -> Vec<Option<i32>> {
    let mut out = Vec::new();
    let mut queue = VecDeque::from([root.clone()]);
    while let Some(slot) = queue.pop_front() {
        match slot {
            Some(node) => {
                let n = node.borrow();
                out.push(Some(n.val));
                queue.push_back(n.left.clone());
                queue.push_back(n.right.clone());
            }
            None => out.push(None),
        }
    }
    while out.last() == Some(&None) {
        out.pop();
    }
    out
}

pub fn min_depth(root: Option<Rc<RefCell<TreeNode>>>) -> usize {
    let Some(node) = root else { return 0 };
    let n = node.borrow();
    match (n.left.clone(), n.right.clone()) {
        (None, None) => 1,
        // A node with one child is not a leaf: the path has to go through that child.
        (Some(child), None) | (None, Some(child)) => 1 + min_depth(Some(child)),
        (left, right) => 1 + min_depth(left).min(min_depth(right)),
    }
}
