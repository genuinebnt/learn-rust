use solution::*;

#[test]
fn zeros() {
    let root = tree(&[Some(0), Some(0), Some(0)]);
    add_path_sums(&root);
    check!(r#"root = [0,0,0]"#, level_order_values(&root), vec![Some(0), Some(0), Some(0)]);
}

#[test]
fn perfect_seven() {
    let root = tree(&[Some(1), Some(2), Some(3), Some(4), Some(5), Some(6), Some(7)]);
    add_path_sums(&root);
    check!(r#"root = [1,2,3,4,5,6,7]"#, level_order_values(&root), vec![Some(1), Some(3), Some(4), Some(7), Some(8), Some(10), Some(11)]);
}

#[test]
fn cancels_out() {
    let root = tree(&[Some(10), None, Some(-10), None, Some(5)]);
    add_path_sums(&root);
    check!(r#"root = [10,null,-10,null,5]"#, level_order_values(&root), vec![Some(10), None, Some(0), None, Some(5)]);
}

#[test]
fn single_negative() {
    let root = tree(&[Some(-3)]);
    add_path_sums(&root);
    check!(r#"root = [-3]"#, level_order_values(&root), vec![Some(-3)]);
}

#[test]
fn siblings_are_independent() {
    let root = tree(&[Some(1), Some(2), Some(3), Some(4), None, None, Some(5)]);
    add_path_sums(&root);
    check!(r#"root = [1,2,3,4,null,null,5]"#, level_order_values(&root), vec![Some(1), Some(3), Some(4), Some(7), None, None, Some(9)]);
}

#[test]
fn left_path() {
    let root = tree(&[Some(1), Some(1), None, Some(1), None, Some(1)]);
    add_path_sums(&root);
    check!(r#"root = [1,1,null,1,null,1]"#, level_order_values(&root), vec![Some(1), Some(2), None, Some(3), None, Some(4)]);
}

#[test]
fn twice() {
    let root = tree(&[Some(1), Some(2)]);
    add_path_sums(&root);
    add_path_sums(&root);
    check!(r#"root = [1,2] summed twice"#, level_order_values(&root), vec![Some(1), Some(4)]);
}

#[test]
fn large_values() {
    let root = tree(&[Some(1000000), Some(1000000), Some(1000000)]);
    add_path_sums(&root);
    check!(r#"root = [1000000,1000000,1000000]"#, level_order_values(&root), vec![Some(1000000), Some(2000000), Some(2000000)]);
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

/// The expected level order: BFS carrying the sum from the root.
fn expected(root: &Option<Rc<RefCell<TreeNode>>>) -> Vec<Option<i32>> {
    let mut out = Vec::new();
    let mut queue = std::collections::VecDeque::from([(root.clone(), 0)]);
    while let Some((slot, above)) = queue.pop_front() {
        match slot {
            Some(n) => {
                let n = n.borrow();
                out.push(Some(above + n.val));
                queue.push_back((n.left.clone(), above + n.val));
                queue.push_back((n.right.clone(), above + n.val));
            }
            None => out.push(None),
        }
    }
    while out.last() == Some(&None) {
        out.pop();
    }
    out
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(608);
    for _ in 0..300 {
        let n = rng.below(14);
        let root = random_tree(&mut rng, n, -9, 9);
        let (input, want) = (show(&root), expected(&root));
        add_path_sums(&root);
        check!(format!("root = {input}"), level_order_values(&root), want);
    }
}

#[test]
fn scale_path_50000() {
    let got = big_stack(|| {
        let root = path(50_000, true);
        add_path_sums(&root);
        let mut node = root;
        let mut last = 0;
        while let Some(n) = node {
            last = n.borrow().val;
            node = n.borrow().left.clone();
        }
        last
    });
    check!("root = left path 1..=50000 (the bottom value becomes 1 + 2 + … + 50000)", got, 1_250_025_000);
}
