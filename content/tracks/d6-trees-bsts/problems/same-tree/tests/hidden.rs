use solution::*;

#[test]
fn single_same() {
    check!(r#"p = [1], q = [1]"#, is_same_tree(tree(&[Some(1)]), tree(&[Some(1)])), true);
}

#[test]
fn single_different() {
    check!(r#"p = [1], q = [2]"#, is_same_tree(tree(&[Some(1)]), tree(&[Some(2)])), false);
}

#[test]
fn mirror_is_not_same() {
    check!(r#"p = [1,2,3], q = [1,3,2]"#, is_same_tree(tree(&[Some(1), Some(2), Some(3)]), tree(&[Some(1), Some(3), Some(2)])), false);
}

#[test]
fn deep_shape_differs() {
    check!(r#"p = [1,2,3,4], q = [1,2,3,null,4]"#, is_same_tree(tree(&[Some(1), Some(2), Some(3), Some(4)]), tree(&[Some(1), Some(2), Some(3), None, Some(4)])), false);
}

#[test]
fn extra_node_at_the_bottom() {
    check!(r#"p = [1,2,3], q = [1,2,3,null,null,null,4]"#, is_same_tree(tree(&[Some(1), Some(2), Some(3)]), tree(&[Some(1), Some(2), Some(3), None, None, None, Some(4)])), false);
}

#[test]
fn negatives_same() {
    check!(r#"p = [-1,-2,null,-3], q = [-1,-2,null,-3]"#, is_same_tree(tree(&[Some(-1), Some(-2), None, Some(-3)]), tree(&[Some(-1), Some(-2), None, Some(-3)])), true);
}

#[test]
fn second_empty() {
    check!(r#"p = [0], q = []"#, is_same_tree(tree(&[Some(0)]), None), false);
}

#[test]
fn extremes() {
    check!(r#"p = [i32::MIN,null,i32::MAX], q = [i32::MIN,null,i32::MAX]"#, is_same_tree(tree(&[Some(i32::MIN), None, Some(i32::MAX)]), tree(&[Some(i32::MIN), None, Some(i32::MAX)])), true);
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
    let mut rng = anneal_prelude::Rng::new(603);
    for _ in 0..300 {
        let n = rng.below(8);
        let p = random_tree(&mut rng, n, 0, 2);
        // Half the time compare against an exact copy.
        let q = if rng.bool() { tree(&level_order_values(&p)) } else { let m = rng.below(8); random_tree(&mut rng, m, 0, 2) };
        let want = level_order_values(&p) == level_order_values(&q);
        check!(format!("p = {}, q = {}", show(&p), show(&q)), is_same_tree(p.clone(), q.clone()), want);
    }
}

#[test]
fn scale_perfect_131071() {
    let n = (1 << 17) - 1;
    let mut values: Vec<Option<i32>> = (1..=n).map(Some).collect();
    let same = is_same_tree(tree(&values), tree(&values));
    values[n as usize - 1] = Some(0);
    let differs_last = is_same_tree(complete(n as usize), tree(&values));
    check!("two complete trees of 2^17 - 1 nodes, then the second with its last value changed", (same, differs_last), (true, false));
}

#[test]
fn scale_paths_50000() {
    let got = big_stack(|| (is_same_tree(path(50_000, true), path(50_000, true)), is_same_tree(path(50_000, true), path(50_000, false))));
    check!("two left paths of 50000 nodes; a left path against a right path", got, (true, false));
}
