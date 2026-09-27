use solution::*;

use std::collections::HashMap;
use std::rc::Rc;

/// Every node reachable from `start` (BFS, no recursion): sorted (val, neighbour vals), plus the node addresses.
fn shape(start: &NodeRef) -> (Vec<(i32, Vec<i32>)>, Vec<usize>) {
    let mut index: HashMap<usize, usize> = HashMap::new();
    let mut nodes = vec![Rc::clone(start)];
    index.insert(Rc::as_ptr(start) as usize, 0);
    let mut i = 0;
    while i < nodes.len() {
        let cur = Rc::clone(&nodes[i]);
        i += 1;
        for nb in &cur.borrow().neighbors {
            let key = Rc::as_ptr(nb) as usize;
            if !index.contains_key(&key) {
                index.insert(key, nodes.len());
                nodes.push(Rc::clone(nb));
            }
        }
    }
    let mut out: Vec<(i32, Vec<i32>)> = nodes.iter().map(|x| (x.borrow().val, x.borrow().neighbors.iter().map(|y| y.borrow().val).collect())).collect();
    out.sort();
    (out, nodes.iter().map(|x| Rc::as_ptr(x) as usize).collect())
}

#[test]
fn independent() {
    let a = node(1);
    let b = node(2);
    link(&a, &b);
    let c = clone_graph(&a);
    c.borrow_mut().val = 9;
    let v = a.borrow().val;
    check!(r#"1-2; clone, set copy's val to 9; original val"#, v, 1);
}

#[test]
fn self_loop() {
    let a = node(1);
    link(&a, &a);
    let c = clone_graph(&a);
    let first = std::rc::Rc::clone(&c.borrow().neighbors[0]);
    let same = std::rc::Rc::ptr_eq(&first, &c) && c.borrow().neighbors.len() == 2;
    check!(r#"1 linked to itself"#, same, true);
}

#[test]
fn lonely() {
    let c = clone_graph(&node(7));
    let n = (c.borrow().val, c.borrow().neighbors.len());
    check!(r#"a single node"#, n, (7, 0));
}

#[test]
fn clone_from_middle() {
    let n: Vec<NodeRef> = (1..=3).map(node).collect();
    link(&n[0], &n[1]);
    link(&n[1], &n[2]);
    let c = clone_graph(&n[1]);
    check!(r#"path 1-2-3; clone from 2"#, shape(&c).0, vec![(1, vec![2]), (2, vec![1, 3]), (3, vec![2])]);
}

#[test]
fn original_untouched() {
    let (a, b, d) = (node(1), node(2), node(3));
    link(&a, &b);
    link(&b, &d);
    link(&d, &a);
    let c = clone_graph(&a);
    let c2 = Rc::clone(&c.borrow().neighbors[0]);
    link(&c, &c2);
    check!(r#"1-2-3 triangle; clone, then add a link inside the copy; original shape"#, shape(&a).0, vec![(1, vec![2, 3]), (2, vec![1, 3]), (3, vec![2, 1])]);
}

#[test]
fn complete_k5_negative_values() {
    let n: Vec<NodeRef> = (1..=5).map(|v| node(-v)).collect();
    for i in 0..5 {
        for j in i + 1..5 {
            link(&n[i], &n[j]);
        }
    }
    let orig = shape(&n[2]);
    let got = shape(&clone_graph(&n[2]));
    check!(r#"K5 on values -1..=-5; clone from -3"#, (got.0, got.1.iter().any(|p| orig.1.contains(p))), (orig.0.clone(), false));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(906);
    for _ in 0..200 {
        let n = 1 + rng.below(7);
        let m = rng.below(12);
        let nodes: Vec<NodeRef> = (0..n as i32).map(node).collect();
        let mut edges = Vec::new();
        for _ in 0..m {
            let (a, b) = (rng.below(n), rng.below(n));
            edges.push((a, b));
            link(&nodes[a], &nodes[b]);
        }
        let start = rng.below(n);
        let want = shape(&nodes[start]);
        let got = shape(&clone_graph(&nodes[start]));
        let shared = got.1.iter().any(|p| want.1.contains(p));
        check!(format!("n = {n}, edges = {edges:?}, start = {start}"), (got.0, shared), (want.0, false));
    }
}

#[test]
fn scale_path_100k() {
    let nodes: Vec<NodeRef> = (0..100_000).map(node).collect();
    for i in 1..nodes.len() {
        link(&nodes[i - 1], &nodes[i]);
    }
    let (got, _) = shape(&clone_graph(&nodes[0]));
    check!("path 0-1-…-99999; clone from 0", (got.len(), got[99_999].clone()), (100_000, (99_999, vec![99_998])));
}
