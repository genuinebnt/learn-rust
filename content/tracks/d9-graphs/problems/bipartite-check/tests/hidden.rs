use solution::*;

#[test]
fn odd_cycle_elsewhere() {
    check!(r#"adj = [[], [2, 3], [1, 3], [1, 2]]"#, is_bipartite(&[vec![], vec![2, 3], vec![1, 3], vec![1, 2]]), false);
}

#[test]
fn two_edges() {
    check!(r#"adj = [[1], [0], [3], [2]]"#, is_bipartite(&[vec![1], vec![0], vec![3], vec![2]]), true);
}

#[test]
fn empty() {
    check!(r#"adj = []"#, is_bipartite(&[]), true);
}

#[test]
fn self_loop() {
    check!(r#"adj = [[0]]"#, is_bipartite(&[vec![0]]), false);
}

#[test]
fn five_cycle() {
    check!(r#"adj = [[1, 4], [0, 2], [1, 3], [2, 4], [3, 0]]"#, is_bipartite(&[vec![1, 4], vec![0, 2], vec![1, 3], vec![2, 4], vec![3, 0]]), false);
}

#[test]
fn six_cycle() {
    check!(r#"cycle 0-1-2-3-4-5-0"#, is_bipartite(&[vec![1, 5], vec![0, 2], vec![1, 3], vec![2, 4], vec![3, 5], vec![4, 0]]), true);
}

#[test]
fn repeated_edges() {
    check!(r#"adj = [[1, 1], [0, 0]]"#, is_bipartite(&[vec![1, 1], vec![0, 0]]), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(930);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let m = rng.below(9);
        let mut adj = vec![Vec::new(); n];
        for _ in 0..m {
            let (a, b) = (rng.below(n), rng.below(n));
            adj[a].push(b);
            if a != b {
                adj[b].push(a);
            }
        }
        // Brute force: try every 2-colouring.
        let want = (0..1u32 << n).any(|mask| (0..n).all(|u| adj[u].iter().all(|&v| (mask >> u & 1) != (mask >> v & 1))));
        check!(format!("adj = {adj:?}"), is_bipartite(&adj), want);
    }
}

#[test]
fn scale_long_path() {
    let n: usize = 200_000;
    let adj: Vec<Vec<usize>> = (0..n).map(|u| [u.wrapping_sub(1), u + 1].into_iter().filter(|&v| v < n).collect()).collect();
    check!("path of 200000 nodes", is_bipartite(&adj), true);
}

#[test]
fn scale_odd_cycle_far_away() {
    // A path of 199999 nodes whose last node closes a triangle with 199997.
    let n: usize = 200_000;
    let mut adj: Vec<Vec<usize>> = (0..n).map(|u| [u.wrapping_sub(1), u + 1].into_iter().filter(|&v| v < n).collect()).collect();
    adj[n - 1].push(n - 3);
    adj[n - 3].push(n - 1);
    check!("path of 200000 nodes plus the edge 199999-199997", is_bipartite(&adj), false);
}
