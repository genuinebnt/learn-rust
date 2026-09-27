use solution::*;

#[test]
fn alone() {
    check!(r#"adj = [[]], start = 0"#, count_reachable(&[vec![]], 0), 1);
}

#[test]
fn self_loop() {
    check!(r#"adj = [[0], []], start = 0"#, count_reachable(&[vec![0], vec![]], 0), 1);
}

#[test]
fn duplicate_edges() {
    check!(r#"adj = [[1, 1, 1], [0, 0]], start = 0"#, count_reachable(&[vec![1, 1, 1], vec![0, 0]], 0), 2);
}

#[test]
fn other_component() {
    check!(r#"adj = [[1], [0], [3], [2]], start = 2"#, count_reachable(&[vec![1], vec![0], vec![3], vec![2]], 2), 2);
}

#[test]
fn star() {
    check!(r#"adj = [[1, 2, 3, 4], [], [], [], []], start = 0"#, count_reachable(&[vec![1, 2, 3, 4], vec![], vec![], vec![], vec![]], 0), 5);
}

#[test]
fn chain_5000() {
    let adj: Vec<Vec<usize>> = (0..5000).map(|i| if i + 1 < 5000 { vec![i + 1] } else { vec![] }).collect();
    check!(r#"path 0 → 1 → … → 4999, start = 0"#, count_reachable(&adj, 0), 5000);
}

#[test]
fn many_paths() {
    let adj: Vec<Vec<usize>> = (0..60).map(|u| if u / 2 < 29 { vec![u / 2 * 2 + 2, u / 2 * 2 + 3] } else { vec![] }).collect();
    check!(r#"30 layers of 2 nodes, each node → both nodes of the next layer; start = 0"#, count_reachable(&adj, 0), 59);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(907);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let adj: Vec<Vec<usize>> = (0..n).map(|_| { let k = rng.below(4); (0..k).map(|_| rng.below(n)).collect() }).collect();
        let start = rng.below(n);
        let mut seen = vec![false; n];
        seen[start] = true;
        let mut todo = vec![start];
        while let Some(u) = todo.pop() {
            for &v in &adj[u] {
                if !seen[v] {
                    seen[v] = true;
                    todo.push(v);
                }
            }
        }
        let want = seen.iter().filter(|&&s| s).count();
        check!(format!("adj = {adj:?}, start = {start}"), count_reachable(&adj, start), want);
    }
}
