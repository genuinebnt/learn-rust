use solution::*;

#[test]
fn parallel_edges() {
    check!(r#"n = 2, edges = [(0,1), (1,0)]"#, critical_connections(2, &[(0, 1), (1, 0)]), Vec::<(usize, usize)>::new());
}

#[test]
fn two_triangles() {
    check!(r#"triangles 0-1-2 and 3-4-5 joined by 2-3"#, critical_connections(6, &[(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3)]), vec![(2, 3)]);
}

#[test]
fn path() {
    check!(r#"n = 4, path 0-1-2-3"#, critical_connections(4, &[(0, 1), (1, 2), (2, 3)]), vec![(0, 1), (1, 2), (2, 3)]);
}

#[test]
fn no_edges() {
    check!(r#"n = 1, edges = []"#, critical_connections(1, &[]), Vec::<(usize, usize)>::new());
}

#[test]
fn several_components() {
    check!(r#"n = 5, edges = [(0,1), (2,3), (3,4), (4,2)]"#, critical_connections(5, &[(0, 1), (2, 3), (3, 4), (4, 2)]), vec![(0, 1)]);
}

#[test]
fn self_loop() {
    check!(r#"n = 2, edges = [(0,0), (0,1)]"#, critical_connections(2, &[(0, 0), (0, 1)]), vec![(0, 1)]);
}

#[test]
fn star() {
    check!(r#"n = 4, edges = [(3,0), (0,1), (2,0)]"#, critical_connections(4, &[(3, 0), (0, 1), (2, 0)]), vec![(0, 1), (0, 2), (0, 3)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(928);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = rng.below(9);
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        // Brute force: an edge is a bridge if removing it leaves its ends disconnected.
        let joined_without = |skip: usize| {
            let (a, b) = edges[skip];
            let mut seen = vec![false; n];
            seen[a] = true;
            let mut stack = vec![a];
            while let Some(u) = stack.pop() {
                for (i, &(x, y)) in edges.iter().enumerate() {
                    for (p, q) in [(x, y), (y, x)] {
                        if i != skip && p == u && !seen[q] {
                            seen[q] = true;
                            stack.push(q);
                        }
                    }
                }
            }
            seen[b]
        };
        let mut want: Vec<(usize, usize)> = (0..m).filter(|&i| !joined_without(i)).map(|i| (edges[i].0.min(edges[i].1), edges[i].0.max(edges[i].1))).collect();
        want.sort_unstable();
        check!(format!("n = {n}, edges = {edges:?}"), critical_connections(n, &edges), want);
    }
}

#[test]
fn cycle_then_path_5000() {
    // A cycle through 0..2500, then a path 2499-2500-…-4999.
    let mut edges: Vec<(usize, usize)> = (0..2500).map(|i| (i, (i + 1) % 2500)).collect();
    edges.extend((2499..4999).map(|i| (i, i + 1)));
    let out = critical_connections(5000, &edges);
    check!("n = 5000, cycle on 0..2500 plus a path to 4999", (out.len(), out[0], out[2499]), (2500, (2499, 2500), (4998, 4999)));
}
