use solution::*;

#[test]
fn right_child_moves_left() {
    check!(r#"root = [1,null,2]"#, level_order_values(&invert_tree(tree(&[Some(1), None, Some(2)]))), vec![Some(1), Some(2)]);
}

#[test]
fn every_level_swaps() {
    check!(r#"root = [1,2,3,4,5]"#, level_order_values(&invert_tree(tree(&[Some(1), Some(2), Some(3), Some(4), Some(5)]))), vec![Some(1), Some(3), Some(2), None, None, Some(5), Some(4)]);
}

#[test]
fn twice_is_identity() {
    check!(r#"root = [5,3,8,1,4,null,9] inverted twice"#, level_order_values(&invert_tree(invert_tree(tree(&[Some(5), Some(3), Some(8), Some(1), Some(4), None, Some(9)])))), vec![Some(5), Some(3), Some(8), Some(1), Some(4), None, Some(9)]);
}

#[test]
fn negatives() {
    check!(r#"root = [-1,-2,-3,null,-4]"#, level_order_values(&invert_tree(tree(&[Some(-1), Some(-2), Some(-3), None, Some(-4)]))), vec![Some(-1), Some(-3), Some(-2), None, None, Some(-4)]);
}

#[test]
fn four_levels() {
    check!(r#"root = [1,2,null,3,null,4]"#, level_order_values(&invert_tree(tree(&[Some(1), Some(2), None, Some(3), None, Some(4)]))), vec![Some(1), None, Some(2), None, Some(3), None, Some(4)]);
}

#[test]
fn same_values() {
    check!(r#"root = [7,7,7,7]"#, level_order_values(&invert_tree(tree(&[Some(7), Some(7), Some(7), Some(7)]))), vec![Some(7), Some(7), Some(7), None, None, None, Some(7)]);
}

#[test]
fn returns_the_same_root() {
    let root = tree(&[Some(1), Some(2), Some(3)]);
    check!(r#"root = [1,2,3]"#, Rc::ptr_eq(&root.clone().unwrap(), &invert_tree(root.clone()).unwrap()), true);
}

#[test]
fn extremes() {
    check!(r#"root = [0,i32::MIN,i32::MAX]"#, level_order_values(&invert_tree(tree(&[Some(0), Some(i32::MIN), Some(i32::MAX)]))), vec![Some(0), Some(i32::MAX), Some(i32::MIN)]);
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
    // Build a mirrored copy with new nodes.
    fn mirror(node: &Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
        node.as_ref().map(|n| {
            let n = n.borrow();
            Rc::new(RefCell::new(TreeNode { val: n.val, left: mirror(&n.right), right: mirror(&n.left) }))
        })
    }
    let mut rng = anneal_prelude::Rng::new(604);
    for _ in 0..300 {
        let n = rng.below(16);
        let root = random_tree(&mut rng, n, -9, 9);
        let (input, want) = (show(&root), level_order_values(&mirror(&root)));
        check!(format!("root = {input}"), level_order_values(&invert_tree(root)), want);
    }
}

#[test]
fn scale_perfect_131071() {
    let n: i32 = (1 << 17) - 1;
    // Each level of a mirrored complete tree is that level reversed.
    let mut want = Vec::new();
    for d in 0..17 {
        want.extend((1 << d..1 << (d + 1)).rev().map(Some));
    }
    check!("root = complete tree of 2^17 - 1 nodes", level_order_values(&invert_tree(complete(n as usize))) == want, true);
}

#[test]
fn scale_path_50000() {
    let got = big_stack(|| {
        let mut node = invert_tree(path(50_000, true));
        let mut count = 0;
        while let Some(n) = node {
            assert!(n.borrow().left.is_none());
            count += 1;
            node = n.borrow().right.clone();
        }
        count
    });
    check!("root = a left path of 50000 nodes (expect a right path)", got, 50_000);
}
