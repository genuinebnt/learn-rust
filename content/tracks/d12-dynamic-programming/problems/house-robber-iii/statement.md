The houses form a binary tree, and each node's `val` is the money in that house. You may
not rob two houses joined directly by an edge (a parent and its child). Return the most
money you can rob. The tree uses LeetCode's `Option<Rc<RefCell<TreeNode>>>` shape and
`tree(&[..])` builds one from LeetCode's level-order form.
