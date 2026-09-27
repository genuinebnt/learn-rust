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

pub fn rob(root: Option<Rc<RefCell<TreeNode>>>) -> i64 {
    // (best with this node robbed, best with it left alone) for the subtree under `node`.
    fn best(node: &Option<Rc<RefCell<TreeNode>>>) -> (i64, i64) {
        let Some(node) = node else { return (0, 0) };
        let node = node.borrow();
        let (left_take, left_skip) = best(&node.left);
        let (right_take, right_skip) = best(&node.right);
        // Robbing this house rules out both children; skipping it leaves each child free.
        let take = node.val as i64 + left_skip + right_skip;
        let skip = left_take.max(left_skip) + right_take.max(right_skip);
        (take, skip)
    }
    let (take, skip) = best(&root);
    take.max(skip)
}
