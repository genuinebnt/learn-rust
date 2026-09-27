use solution::*;

#[test]
fn path_of_four() {
    check!(r#"n = 4, path 3-1-0-2"#, find_min_height_trees(4, &[(3, 1), (1, 0), (0, 2)]), vec![0, 1]);
}

#[test]
fn three_nodes() {
    check!(r#"n = 3, edges = [(2, 0), (0, 1)]"#, find_min_height_trees(3, &[(2, 0), (0, 1)]), vec![0]);
}

#[test]
fn centre_is_not_the_busiest_node() {
    check!(r#"n = 7, edges = [(0, 1), (0, 2), (0, 3), (0, 4), (4, 5), (5, 6)]"#, find_min_height_trees(7, &[(0, 1), (0, 2), (0, 3), (0, 4), (4, 5), (5, 6)]), vec![4]);
}

#[test]
fn broom() {
    check!(r#"n = 6, edges = [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5)]"#, find_min_height_trees(6, &[(0, 1), (1, 2), (2, 3), (3, 4), (3, 5)]), vec![2]);
}

#[test]
fn spider() {
    check!(r#"n = 7, three legs of two from node 0"#, find_min_height_trees(7, &[(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6)]), vec![0]);
}

#[test]
fn big_star() {
    let edges: Vec<(usize, usize)> = (1..100_000).map(|i| (i, 0)).collect();
    check!(r#"n = 100000, 0 joined to every other node"#, find_min_height_trees(100_000, &edges), vec![0]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(947);
    for _ in 0..300 {
        let n = 1 + rng.below(9);
        let mut label: Vec<usize> = (0..n).collect();
        rng.shuffle(&mut label);
        let edges: Vec<(usize, usize)> = (1..n).map(|i| { let j = rng.below(i); (label[i], label[j]) }).collect();
        // Brute force: BFS from every node for its height.
        let mut adj = vec![Vec::new(); n];
        for &(a, b) in &edges {
            adj[a].push(b);
            adj[b].push(a);
        }
        let height = |root: usize| {
            let mut d = vec![usize::MAX; n];
            d[root] = 0;
            let mut q = std::collections::VecDeque::from([root]);
            while let Some(u) = q.pop_front() {
                for &v in &adj[u] {
                    if d[v] == usize::MAX {
                        d[v] = d[u] + 1;
                        q.push_back(v);
                    }
                }
            }
            *d.iter().max().unwrap()
        };
        let h: Vec<usize> = (0..n).map(height).collect();
        let best = *h.iter().min().unwrap();
        let want: Vec<usize> = (0..n).filter(|&u| h[u] == best).collect();
        check!(format!("n = {n}, edges = {edges:?}"), find_min_height_trees(n, &edges), want);
    }
}

#[test]
fn scale_long_path() {
    // A path of 200000 nodes, listed out of order: the centres are 99999 and 100000.
    let n = 200_000;
    let mut edges: Vec<(usize, usize)> = (1..n).map(|i| (i - 1, i)).collect();
    anneal_prelude::Rng::new(948).shuffle(&mut edges);
    check!("path of 200000 nodes", find_min_height_trees(n, &edges), vec![99_999, 100_000]);
}
