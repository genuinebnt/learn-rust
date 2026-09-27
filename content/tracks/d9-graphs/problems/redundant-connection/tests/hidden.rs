use solution::*;

#[test]
fn reversed_pairs() {
    check!(r#"edges = [(2,1), (3,1), (4,2), (1,4)]"#, find_redundant(&[(2, 1), (3, 1), (4, 2), (1, 4)]), Some((1, 4)));
}

#[test]
fn double_edge() {
    check!(r#"edges = [(1,2), (2,1)]"#, find_redundant(&[(1, 2), (2, 1)]), Some((2, 1)));
}

#[test]
fn cycle_after_a_tail() {
    check!(r#"edges = [(1,5), (1,2), (2,3), (3,4), (4,2)]"#, find_redundant(&[(1, 5), (1, 2), (2, 3), (3, 4), (4, 2)]), Some((4, 2)));
}

#[test]
fn every_edge_on_the_cycle() {
    check!(r#"edges = [(3,4), (1,2), (2,4), (3,1)]"#, find_redundant(&[(3, 4), (1, 2), (2, 4), (3, 1)]), Some((3, 1)));
}

#[test]
fn ring_1000() {
    let edges: Vec<(usize, usize)> = (1..=1000).map(|i| (i, i % 1000 + 1)).collect();
    check!(r#"ring 1-2-…-1000-1"#, find_redundant(&edges), Some((1000, 1)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(921);
    for _ in 0..300 {
        let n = 2 + rng.below(7);
        let mut label: Vec<usize> = (1..=n).collect();
        rng.shuffle(&mut label);
        let mut edges: Vec<(usize, usize)> = (1..n).map(|i| { let j = rng.below(i); if rng.bool() { (label[i], label[j]) } else { (label[j], label[i]) } }).collect();
        let a = rng.below(n);
        let b = (a + 1 + rng.below(n - 1)) % n;
        edges.push((label[a], label[b]));
        rng.shuffle(&mut edges);
        // Brute force: the last edge whose removal leaves every node connected.
        let connected_without = |skip: usize| {
            let mut seen = vec![false; n + 1];
            seen[1] = true;
            let mut stack = vec![1];
            while let Some(u) = stack.pop() {
                for (i, &(x, y)) in edges.iter().enumerate() {
                    if i != skip && (x == u || y == u) {
                        let v = if x == u { y } else { x };
                        if !seen[v] {
                            seen[v] = true;
                            stack.push(v);
                        }
                    }
                }
            }
            seen[1..].iter().all(|&s| s)
        };
        let want = (0..edges.len()).rev().find(|&i| connected_without(i)).map(|i| edges[i]);
        check!(format!("edges = {edges:?}"), find_redundant(&edges), want);
    }
}

#[test]
fn scale_star_200k() {
    // 1 joined to every other node, then (2, 3) closes a triangle.
    let n = 200_000;
    let mut edges: Vec<(usize, usize)> = (2..=n).map(|i| (1, i)).collect();
    edges.push((2, 3));
    check!("n = 200000: (1, i) for every i, then (2, 3)", find_redundant(&edges), Some((2, 3)));
}

#[test]
fn scale_cycle_first() {
    // The triangle 1-2-3 comes first; 99997 tree edges follow it.
    let n = 100_000;
    let mut edges = vec![(1, 2), (2, 3), (3, 1)];
    edges.extend((4..=n).map(|i| (i - 1, i)));
    check!("n = 100000: (1,2), (2,3), (3,1), then a path 3-4-…-100000", find_redundant(&edges), Some((3, 1)));
}
