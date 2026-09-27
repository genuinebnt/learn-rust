use solution::*;

#[test]
fn root_itself() {
    check!(r#"parent = [0]; find(0)"#, find(&mut [0], 0), 0);
}

#[test]
fn mid_path() {
    let mut p = vec![1, 2, 2, 0];
    let root = find(&mut p, 3);
    check!(r#"parent = [1, 2, 2, 0]; find(3)"#, (root, p), (2, vec![2, 2, 2, 2]));
}

#[test]
fn union_sequence() {
    let mut p: Vec<usize> = (0..5).collect();
    let r: Vec<bool> = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 0)].into_iter().map(|(a, b)| union(&mut p, a, b)).collect();
    check!(r#"5 singletons; union(0,1), union(1,2), union(0,2), union(3,4), union(4,0)"#, (r, (0..5).all(|i| find(&mut p, i) == find(&mut p, 0))), (vec![true, true, false, true, true], true));
}

#[test]
fn same_set_union_is_false() {
    let mut p = vec![1, 1];
    check!(r#"parent = [1, 1]; union(0, 1)"#, (union(&mut p, 0, 1), p), (false, vec![1, 1]));
}

#[test]
fn union_links_roots_not_nodes() {
    let mut p = vec![1, 1, 3, 3];
    let merged = union(&mut p, 0, 2);
    check!(r#"parent = [1, 1, 3, 3]; union(0, 2)"#, (merged, p), (true, vec![1, 3, 3, 3]));
}

#[test]
fn chain_1000() {
    let mut p: Vec<usize> = (0..1000).map(|i: usize| i.saturating_sub(1)).collect();
    let root = find(&mut p, 999);
    check!(r#"parent[i] = i - 1 for 1000 nodes; find(999)"#, (root, p.iter().all(|&x| x == 0)), (0, true));
}

#[test]
fn deep_node_then_its_ancestor() {
    let mut p = vec![0, 0, 1, 2, 3];
    let a = find(&mut p, 4);
    let b = find(&mut p, 2);
    check!(r#"parent = [0, 0, 1, 2, 3]; find(4), then find(2)"#, (a, b, p), (0, 0, vec![0, 0, 0, 0, 0]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(926);
    for _ in 0..300 {
        let n = 1 + rng.below(9);
        // A random forest: each node points at itself or at a smaller node.
        let parent: Vec<usize> = (0..n).map(|i| if i == 0 || rng.below(4) == 0 { i } else { rng.below(i) }).collect();
        let x = rng.below(n);
        let mut want = parent.clone();
        let mut root = x;
        while want[root] != root {
            root = want[root];
        }
        let mut y = x;
        while want[y] != root {
            let next = want[y];
            want[y] = root;
            y = next;
        }
        let mut got = parent.clone();
        let r = find(&mut got, x);
        check!(format!("parent = {parent:?}; find({x})"), (r, got), (root, want));
    }
}
