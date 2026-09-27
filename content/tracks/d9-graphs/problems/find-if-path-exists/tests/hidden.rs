use solution::*;

#[test]
fn self_loops_only() {
    check!(r#"n = 2, edges = [(0, 0), (1, 1)], source = 0, destination = 1"#, valid_path(2, &[(0, 0), (1, 1)], 0, 1), false);
}

#[test]
fn repeated_edges() {
    check!(r#"n = 3, edges = [(0, 1), (1, 0), (0, 1), (1, 2)], source = 2, destination = 0"#, valid_path(3, &[(0, 1), (1, 0), (0, 1), (1, 2)], 2, 0), true);
}

#[test]
fn isolated_source() {
    check!(r#"n = 4, edges = [(1, 2), (2, 3)], source = 0, destination = 3"#, valid_path(4, &[(1, 2), (2, 3)], 0, 3), false);
}

#[test]
fn reach_backwards_along_a_path() {
    check!(r#"n = 5, edges = [(0, 1), (1, 2), (2, 3), (3, 4)], source = 4, destination = 0"#, valid_path(5, &[(0, 1), (1, 2), (2, 3), (3, 4)], 4, 0), true);
}

#[test]
fn same_node_isolated() {
    check!(r#"n = 3, edges = [(0, 1)], source = 2, destination = 2"#, valid_path(3, &[(0, 1)], 2, 2), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(935);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let m = rng.below(8);
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        let (s, d) = (rng.below(n), rng.below(n));
        // Brute force: grow the reached set until it stops changing.
        let mut reached = vec![false; n];
        reached[s] = true;
        loop {
            let before = reached.iter().filter(|&&r| r).count();
            for &(a, b) in &edges {
                if reached[a] || reached[b] {
                    reached[a] = true;
                    reached[b] = true;
                }
            }
            if reached.iter().filter(|&&r| r).count() == before {
                break;
            }
        }
        check!(format!("n = {n}, edges = {edges:?}, source = {s}, destination = {d}"), valid_path(n, &edges, s, d), reached[d]);
    }
}

#[test]
fn scale_long_path() {
    // A path 0-1-…-199999 listed from the far end; the destination is the last node.
    let n = 200_000;
    let edges: Vec<(usize, usize)> = (1..n).rev().map(|i| (i, i - 1)).collect();
    check!("n = 200000, path 0-1-…-199999, source = 0, destination = 199999", valid_path(n, &edges, 0, n - 1), true);
}

#[test]
fn scale_unreachable() {
    // Two long paths that never meet.
    let n = 200_000;
    let edges: Vec<(usize, usize)> = (2..n).map(|i| (i - 2, i)).collect();
    check!("n = 200000, evens and odds each form a path; source = 0, destination = 199999", valid_path(n, &edges, 0, n - 1), false);
}
