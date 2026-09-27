use solution::*;

#[test]
fn single_match() {
    check!(r#"root = [1], target_sum = 1"#, has_path_sum(tree(&[Some(1)]), 1), true);
}

#[test]
fn single_miss() {
    check!(r#"root = [1], target_sum = 0"#, has_path_sum(tree(&[Some(1)]), 0), false);
}

#[test]
fn right_leaf() {
    check!(r#"root = [1,2,3], target_sum = 4"#, has_path_sum(tree(&[Some(1), Some(2), Some(3)]), 4), true);
}

#[test]
fn zeros_never_sum_to_zero() {
    check!(r#"root = [0,1,1], target_sum = 0"#, has_path_sum(tree(&[Some(0), Some(1), Some(1)]), 0), false);
}

#[test]
fn leetcode_negatives() {
    check!(r#"root = [1,-2,-3,1,3,-2,null,-1], target_sum = -1"#, has_path_sum(tree(&[Some(1), Some(-2), Some(-3), Some(1), Some(3), Some(-2), None, Some(-1)]), -1), true);
}

#[test]
fn overshoot_then_come_back() {
    check!(r#"root = [5,6,-4], target_sum = 1"#, has_path_sum(tree(&[Some(5), Some(6), Some(-4)]), 1), true);
}

#[test]
fn partial_path_does_not_count() {
    check!(r#"root = [1,2,null,3], target_sum = 3"#, has_path_sum(tree(&[Some(1), Some(2), None, Some(3)]), 3), false);
}

#[test]
fn single_zero() {
    check!(r#"root = [0], target_sum = 0"#, has_path_sum(tree(&[Some(0)]), 0), true);
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
    // Every root-to-leaf sum.
    fn sums(node: &Option<Rc<RefCell<TreeNode>>>, above: i32, out: &mut Vec<i32>) {
        if let Some(n) = node {
            let n = n.borrow();
            if n.left.is_none() && n.right.is_none() {
                out.push(above + n.val);
            }
            sums(&n.left, above + n.val, out);
            sums(&n.right, above + n.val, out);
        }
    }
    let mut rng = anneal_prelude::Rng::new(606);
    for _ in 0..400 {
        let n = rng.below(12);
        let root = random_tree(&mut rng, n, -5, 5);
        let target = rng.int(-8, 8) as i32;
        let mut all = Vec::new();
        sums(&root, 0, &mut all);
        check!(format!("root = {}, target_sum = {target}", show(&root)), has_path_sum(root.clone(), target), all.contains(&target));
    }
}

#[test]
fn scale_perfect_131071() {
    // The leaf 131071 is reached through 1, 3, 7, 15, …, 2^k - 1.
    let sum: i32 = (1..=17).map(|k| (1 << k) - 1).sum();
    let root = complete((1 << 17) - 1);
    check!("root = complete tree of 2^17 - 1 nodes, target_sum = sum of the rightmost path, then one more", (has_path_sum(root.clone(), sum), has_path_sum(root, sum + 1)), (true, false));
}

#[test]
fn scale_path_50000() {
    let got = big_stack(|| (has_path_sum(path(50_000, false), 1_250_025_000), has_path_sum(path(50_000, false), 1_250_024_999)));
    check!("root = right path 1..=50000, target_sum = 1250025000; then 1250024999", got, (true, false));
}
