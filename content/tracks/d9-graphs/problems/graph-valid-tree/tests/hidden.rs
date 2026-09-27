use solution::*;

#[test]
fn single() {
    check!(r#"n = 1, edges = []"#, valid_tree(1, &[]), true);
}

#[test]
fn forest() {
    check!(r#"n = 4, edges = [(0,1), (2,3)]"#, valid_tree(4, &[(0, 1), (2, 3)]), false);
}

#[test]
fn right_count_but_cycle() {
    check!(r#"n = 4, edges = [(0,1), (1,0), (2,3)]"#, valid_tree(4, &[(0, 1), (1, 0), (2, 3)]), false);
}

#[test]
fn self_loop() {
    check!(r#"n = 1, edges = [(0,0)]"#, valid_tree(1, &[(0, 0)]), false);
}

#[test]
fn self_loop_with_right_count() {
    check!(r#"n = 2, edges = [(0,0)]"#, valid_tree(2, &[(0, 0)]), false);
}

#[test]
fn path_listed_backwards() {
    check!(r#"n = 4, edges = [(3,2), (2,1), (1,0)]"#, valid_tree(4, &[(3, 2), (2, 1), (1, 0)]), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(922);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = if rng.bool() { n - 1 } else { rng.below(n + 1) };
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        // Brute force: n - 1 edges, and a search from 0 reaches every node.
        let mut seen = vec![false; n];
        seen[0] = true;
        let mut stack = vec![0];
        while let Some(u) = stack.pop() {
            for &(a, b) in &edges {
                for (x, y) in [(a, b), (b, a)] {
                    if x == u && !seen[y] {
                        seen[y] = true;
                        stack.push(y);
                    }
                }
            }
        }
        let want = m + 1 == n && seen.iter().all(|&s| s);
        check!(format!("n = {n}, edges = {edges:?}"), valid_tree(n, &edges), want);
    }
}

#[test]
fn scale_star_200k() {
    let n = 200_000;
    let edges: Vec<(usize, usize)> = (1..n).map(|i| (0, i)).collect();
    check!("n = 200000, 0 joined to every other node", valid_tree(n, &edges), true);
}

#[test]
fn scale_star_plus_one_cycle() {
    let n = 200_000;
    let mut edges: Vec<(usize, usize)> = (1..n - 1).map(|i| (0, i)).collect();
    edges.push((n - 2, 1));
    check!("n = 200000, star missing node 199999, plus (199998, 1)", valid_tree(n, &edges), false);
}
