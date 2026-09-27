use solution::*;
use std::cell::RefCell;
use std::rc::Rc;

#[test]
fn empty() {
    check!(r#"root = []"#, rob(None), 0);
}

#[test]
fn zero() {
    check!(r#"root = [0]"#, rob(tree(&[Some(0)])), 0);
}

#[test]
fn all_zero() {
    check!(r#"root = [0, 0, 0]"#, rob(tree(&[Some(0), Some(0), Some(0)])), 0);
}

#[test]
fn children_beat_root() {
    check!(r#"root = [1, 2, 3]"#, rob(tree(&[Some(1), Some(2), Some(3)])), 5);
}

#[test]
fn root_beats_children() {
    check!(r#"root = [10, 1, 1]"#, rob(tree(&[Some(10), Some(1), Some(1)])), 10);
}

#[test]
fn mix_levels() {
    check!(r#"root = [5, 1, 1, 10, 1, 1, 10]"#, rob(tree(&[Some(5), Some(1), Some(1), Some(10), Some(1), Some(1), Some(10)])), 27);
}

#[test]
fn right_heavy() {
    check!(r#"root = [2, 1, 3, null, 4]"#, rob(tree(&[Some(2), Some(1), Some(3), None, Some(4)])), 7);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1257);
    for _ in 0..300 {
        let n = rng.below(12);
        let mut vals: Vec<Option<i32>> = Vec::new();
        for i in 0..n {
            let present = i == 0 || rng.below(4) > 0;
            let v = rng.int(0, 20) as i32;
            vals.push(present.then_some(v));
        }
        let root = tree(&vals);
        // Flatten to (value, parent) and try every set of houses with no parent-child pair.
        let mut nodes: Vec<(i64, Option<usize>)> = Vec::new();
        let mut todo = vec![(root.clone(), None)];
        while let Some((slot, parent)) = todo.pop() {
            if let Some(node) = slot {
                let node = node.borrow();
                nodes.push((node.val as i64, parent));
                let me = nodes.len() - 1;
                todo.push((node.left.clone(), Some(me)));
                todo.push((node.right.clone(), Some(me)));
            }
        }
        let mut want = 0;
        for mask in 0..1u32 << nodes.len() {
            let ok = (0..nodes.len()).all(|i| mask >> i & 1 == 0 || nodes[i].1.map_or(true, |p| mask >> p & 1 == 0));
            if ok {
                want = want.max((0..nodes.len()).filter(|&i| mask >> i & 1 == 1).map(|i| nodes[i].0).sum::<i64>());
            }
        }
        check!(format!("root = {vals:?}"), rob(root), want);
    }
}

#[test]
fn scale_complete_262143() {
    let vals: Vec<Option<i32>> = (0..262_143i64).map(|i| Some((i * 7919 % 10001) as i32)).collect();
    check!("complete tree, val[i] = (7919·i) % 10001 in level order, 2^18 - 1 nodes", rob(tree(&vals)), 884_341_031);
}

#[test]
fn scale_complete_past_i32() {
    let vals: Vec<Option<i32>> = vec![Some(10_000); 262_143];
    check!("complete tree of 2^18 - 1 houses worth 10000", rob(tree(&vals)), 1_747_620_000);
}

#[test]
fn deep_path_100000() {
    // A left-leaning path is 100000 levels deep: run on a thread with a big stack.
    let got = std::thread::Builder::new()
        .stack_size(512 << 20)
        .spawn(|| {
            let mut below = None;
            for v in (1..=100_000).rev() {
                let mut node = TreeNode::new(v);
                node.left = below;
                below = Some(Rc::new(RefCell::new(node)));
            }
            rob(below)
        })
        .unwrap()
        .join()
        .unwrap();
    check!("path 1 → 2 → … → 100000 (each the left child)", got, 2_500_050_000);
}
