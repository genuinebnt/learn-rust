use solution::*;

#[test]
fn leaf_on_the_right() {
    check!(r#"root = [1,2,3,4]"#, min_depth(tree(&[Some(1), Some(2), Some(3), Some(4)])), 2);
}

#[test]
fn right_child_only() {
    check!(r#"root = [1,null,2]"#, min_depth(tree(&[Some(1), None, Some(2)])), 2);
}

#[test]
fn perfect_seven() {
    check!(r#"root = [1,2,3,4,5,6,7]"#, min_depth(tree(&[Some(1), Some(2), Some(3), Some(4), Some(5), Some(6), Some(7)])), 3);
}

#[test]
fn left_path() {
    check!(r#"root = [1,2,null,3]"#, min_depth(tree(&[Some(1), Some(2), None, Some(3)])), 3);
}

#[test]
fn shallow_left_leaf() {
    check!(r#"root = [1,2,3,null,null,4,5]"#, min_depth(tree(&[Some(1), Some(2), Some(3), None, None, Some(4), Some(5)])), 2);
}

#[test]
fn negatives() {
    check!(r#"root = [-1,-2]"#, min_depth(tree(&[Some(-1), Some(-2)])), 2);
}

#[test]
fn one_child_below_a_fork() {
    check!(r#"root = [1,2,3,4,null,null,5,6,null,null,7]"#, min_depth(tree(&[Some(1), Some(2), Some(3), Some(4), None, None, Some(5), Some(6), None, None, Some(7)])), 4);
}

#[test]
fn deep_leaf_only_on_one_side() {
    check!(r#"root = [1,null,2,3]"#, min_depth(tree(&[Some(1), None, Some(2), Some(3)])), 3);
}

use std::cell::RefCell;
use std::rc::Rc;

/// Runs `f` on a thread with a 256 MB stack, for trees too deep for the default 2 MB.
#[allow(dead_code)]
fn big_stack<R: Send + 'static>(f: impl FnOnce() -> R + Send + 'static) -> R {
    std::thread::Builder::new().stack_size(256 << 20).spawn(f).unwrap().join().unwrap()
}

/// A random tree shape with `n` nodes and values in `lo..=hi`.
#[allow(dead_code)]
fn random_tree(rng: &mut anneal_prelude::Rng, n: usize, lo: i64, hi: i64) -> Option<Rc<RefCell<TreeNode>>> {
    if n == 0 {
        return None;
    }
    let v = rng.int(lo, hi) as i32;
    let root = Rc::new(RefCell::new(TreeNode::new(v)));
    let mut open = vec![(root.clone(), true), (root.clone(), false)];
    for _ in 1..n {
        let i = rng.below(open.len());
        let (parent, left) = open.swap_remove(i);
        let v = rng.int(lo, hi) as i32;
        let child = Rc::new(RefCell::new(TreeNode::new(v)));
        if left {
            parent.borrow_mut().left = Some(child.clone());
        } else {
            parent.borrow_mut().right = Some(child.clone());
        }
        open.push((child.clone(), true));
        open.push((child, false));
    }
    Some(root)
}

/// A path of `n` nodes valued 1..=n from the top, each the left (or right) child of the one above.
#[allow(dead_code)]
fn path(n: usize, left: bool) -> Option<Rc<RefCell<TreeNode>>> {
    let mut below = None;
    for v in (1..=n as i32).rev() {
        let mut node = TreeNode::new(v);
        if left {
            node.left = below;
        } else {
            node.right = below;
        }
        below = Some(Rc::new(RefCell::new(node)));
    }
    below
}

/// The complete tree with values 1..=n in level order.
#[allow(dead_code)]
fn complete(n: usize) -> Option<Rc<RefCell<TreeNode>>> {
    tree(&(1..=n as i32).map(Some).collect::<Vec<_>>())
}

/// LeetCode's text form, e.g. `[3,9,20,null,null,15,7]`.
#[allow(dead_code)]
fn show(root: &Option<Rc<RefCell<TreeNode>>>) -> String {
    let parts: Vec<String> = level_order_values(root).iter().map(|v| v.map_or("null".to_string(), |x| x.to_string())).collect();
    format!("[{}]", parts.join(","))
}

#[test]
fn random_vs_brute_force() {
    // BFS down to the first node with no children.
    let first_leaf = |root: &Option<Rc<RefCell<TreeNode>>>| {
        let mut level: Vec<Rc<RefCell<TreeNode>>> = root.iter().cloned().collect();
        let mut depth = 0;
        while !level.is_empty() {
            depth += 1;
            if level.iter().any(|n| n.borrow().left.is_none() && n.borrow().right.is_none()) {
                return depth;
            }
            level = level.iter().flat_map(|n| {
                let n = n.borrow();
                [n.left.clone(), n.right.clone()]
            }).flatten().collect();
        }
        depth
    };
    let mut rng = anneal_prelude::Rng::new(602);
    for _ in 0..300 {
        let n = rng.below(16);
        let root = random_tree(&mut rng, n, -9, 9);
        check!(format!("root = {}", show(&root)), min_depth(root.clone()), first_leaf(&root));
    }
}

#[test]
fn scale_perfect_131071() {
    check!("root = complete tree of 2^17 - 1 nodes", min_depth(complete((1 << 17) - 1)), 17);
}

#[test]
fn scale_path_50000() {
    let got = big_stack(|| {
        let long = path(50_000, true);
        let root = Some(Rc::new(RefCell::new(TreeNode { val: 0, left: None, right: long.clone() })));
        (min_depth(long), min_depth(root))
    });
    check!("a left path of 50000 nodes; then the same path as the right child of a root with no left child", got, (50_000, 50_001));
}
