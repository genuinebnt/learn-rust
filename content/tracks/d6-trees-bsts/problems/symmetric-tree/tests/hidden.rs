use solution::*;

#[test]
fn inorder_palindrome_trap() {
    check!(r#"root = [1,2,2,2,null,2]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), Some(2), None, Some(2)])), false);
}

#[test]
fn inner_children_mirror() {
    check!(r#"root = [1,2,2,null,3,3]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), None, Some(3), Some(3)])), true);
}

#[test]
fn one_child() {
    check!(r#"root = [1,2]"#, is_symmetric(tree(&[Some(1), Some(2)])), false);
}

#[test]
fn negatives() {
    check!(r#"root = [1,-2,-2]"#, is_symmetric(tree(&[Some(1), Some(-2), Some(-2)])), true);
}

#[test]
fn outer_children_mirror() {
    check!(r#"root = [1,2,2,3,null,null,3]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), Some(3), None, None, Some(3)])), true);
}

#[test]
fn four_levels() {
    check!(r#"root = [1,2,2,3,4,4,3,5,6,7,8,8,7,6,5]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), Some(3), Some(4), Some(4), Some(3), Some(5), Some(6), Some(7), Some(8), Some(8), Some(7), Some(6), Some(5)])), true);
}

#[test]
fn equal_halves_are_not_mirrors() {
    check!(r#"root = [1,2,2,3,4,3,4]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), Some(3), Some(4), Some(3), Some(4)])), false);
}

#[test]
fn same_shape_values_differ_deep() {
    check!(r#"root = [1,2,2,3,4,4,5]"#, is_symmetric(tree(&[Some(1), Some(2), Some(2), Some(3), Some(4), Some(4), Some(5)])), false);
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

/// A copy with left and right swapped everywhere.
fn mirrored(node: &Option<Rc<RefCell<TreeNode>>>) -> Option<Rc<RefCell<TreeNode>>> {
    node.as_ref().map(|n| {
        let n = n.borrow();
        Rc::new(RefCell::new(TreeNode { val: n.val, left: mirrored(&n.right), right: mirrored(&n.left) }))
    })
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(605);
    for _ in 0..300 {
        let n = rng.below(7);
        let half = random_tree(&mut rng, n, 0, 2);
        // Half the time build a symmetric tree, sometimes with one value nudged.
        let right = if rng.bool() { mirrored(&half) } else { let m = rng.below(7); random_tree(&mut rng, m, 0, 2) };
        if rng.below(4) == 0 {
            if let Some(r) = &right {
                r.borrow_mut().val += 1;
            }
        }
        let root = Some(Rc::new(RefCell::new(TreeNode { val: 0, left: half, right })));
        let want = level_order_values(&root) == level_order_values(&mirrored(&root));
        check!(format!("root = {}", show(&root)), is_symmetric(root.clone()), want);
    }
}

#[test]
fn scale_perfect_131071() {
    // Every node on level d holds d, so the tree mirrors itself.
    let values: Vec<Option<i32>> = (0..17).flat_map(|d| std::iter::repeat(Some(d)).take(1 << d)).collect();
    let mut odd = values.clone();
    let last = odd.len() - 1;
    odd[last] = Some(99);
    check!("perfect tree of 2^17 - 1 nodes with value = depth; then its last value changed", (is_symmetric(tree(&values)), is_symmetric(tree(&odd))), (true, false));
}

#[test]
fn scale_paths_50000() {
    let got = big_stack(|| {
        let root = Some(Rc::new(RefCell::new(TreeNode { val: 0, left: path(25_000, true), right: path(25_000, false) })));
        is_symmetric(root)
    });
    check!("root with a left path and a right path of 25000 nodes each", got, true);
}
