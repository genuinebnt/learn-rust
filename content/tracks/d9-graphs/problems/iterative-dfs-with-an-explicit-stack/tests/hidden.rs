use solution::*;

#[test]
fn cycle() {
    check!(r#"adj = [[1], [2], [0]], start = 1"#, dfs_order(&[vec![1], vec![2], vec![0]], 1), vec![1, 2, 0]);
}

#[test]
fn long_path() {
    let adj: Vec<Vec<usize>> = (0..200_000).map(|i| if i + 1 < 200_000 { vec![i + 1] } else { vec![] }).collect();
    let order = dfs_order(&adj, 0);
    check!(r#"path 0 → 1 → … → 199999"#, (order.len(), order.last().copied()), (200_000, Some(199_999)));
}

#[test]
fn self_loop_and_repeats() {
    check!(r#"adj = [[0, 1, 1], [0]], start = 0"#, dfs_order(&[vec![0, 1, 1], vec![0]], 0), vec![0, 1]);
}

#[test]
fn complete_k4_from_2() {
    check!(r#"adj = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]], start = 2"#, dfs_order(&[vec![1, 2, 3], vec![0, 2, 3], vec![0, 1, 3], vec![0, 1, 2]], 2), vec![2, 0, 1, 3]);
}

#[test]
fn start_is_last_node() {
    check!(r#"adj = [[], [0], [1, 0]], start = 2"#, dfs_order(&[vec![], vec![0], vec![1, 0]], 2), vec![2, 1, 0]);
}

#[test]
fn backtracks_to_the_root() {
    check!(r#"adj = [[1, 4], [2], [3], [], [5], []], start = 0"#, dfs_order(&[vec![1, 4], vec![2], vec![3], vec![], vec![5], vec![]], 0), vec![0, 1, 2, 3, 4, 5]);
}

#[test]
fn random_vs_brute_force() {
    fn rec(adj: &[Vec<usize>], u: usize, seen: &mut [bool], out: &mut Vec<usize>) {
        seen[u] = true;
        out.push(u);
        for &v in &adj[u] {
            if !seen[v] {
                rec(adj, v, seen, out);
            }
        }
    }
    let mut rng = anneal_prelude::Rng::new(910);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let adj: Vec<Vec<usize>> = (0..n).map(|_| { let k = rng.below(4); (0..k).map(|_| rng.below(n)).collect() }).collect();
        let start = rng.below(n);
        let mut want = Vec::new();
        rec(&adj, start, &mut vec![false; n], &mut want);
        check!(format!("adj = {adj:?}, start = {start}"), dfs_order(&adj, start), want);
    }
}

#[test]
fn scale_star_with_back_edges() {
    // 0 → every node, every node → 0 and → the next node.
    let n = 200_000;
    let adj: Vec<Vec<usize>> = (0..n).map(|u| if u == 0 { (1..n).collect() } else { vec![0, (u + 1) % n] }).collect();
    let order = dfs_order(&adj, 0);
    check!("star of 200000 nodes plus a ring", (order.len(), order[1], order[n - 1]), (n, 1, n - 1));
}
