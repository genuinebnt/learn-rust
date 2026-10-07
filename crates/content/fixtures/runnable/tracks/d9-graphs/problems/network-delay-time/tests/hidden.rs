use solution::network_delay;

#[test]
fn dense_n100() {
    // Nodes 1..=77 are fully connected; 78..=100 have no incoming edges.
    let mut times = Vec::new();
    for u in 1..=77usize {
        for v in 1..=77usize {
            if u != v {
                times.push((u, v, ((u * 7 + v * 13) % 100) as u32));
            }
        }
    }
    check!("n = 100, 5852 edges, nodes 78..=100 unreachable", network_delay(&times, 100, 1), None);
}

#[test]
fn edges_are_directed() {
    check!("times = [(2,1,5)], n = 2, k = 1", network_delay(&[(2, 1, 5)], 2, 1), None);
}

#[test]
fn more_hops_shorter() {
    check!("times = [(1,2,10), (1,3,1), (3,2,1)], n = 3, k = 1", network_delay(&[(1, 2, 10), (1, 3, 1), (3, 2, 1)], 3, 1), Some(2));
}

#[test]
fn source_in_the_middle() {
    check!("times = [(3,1,4), (3,2,2), (2,4,1)], n = 4, k = 3", network_delay(&[(3, 1, 4), (3, 2, 2), (2, 4, 1)], 4, 3), Some(4));
}

#[test]
fn cycle_back_to_source() {
    check!("times = [(1,2,1), (2,3,1), (3,1,1)], n = 3, k = 1", network_delay(&[(1, 2, 1), (2, 3, 1), (3, 1, 1)], 3, 1), Some(2));
}

#[test]
fn only_source_reachable() {
    check!("times = [(2,3,1)], n = 3, k = 1", network_delay(&[(2, 3, 1)], 3, 1), None);
}

#[test]
fn heaviest_chain() {
    let times: Vec<(usize, usize, u32)> = (1..100).map(|u| (u, u + 1, 100)).collect();
    check!("chain 1 → 2 → … → 100, every edge 100 ms", network_delay(&times, 100, 1), Some(9900));
}

#[test]
fn random_vs_bellman_ford() {
    let mut rng = anneal_prelude::Rng::new(42);
    for _ in 0..300 {
        let n = 1 + rng.below(6);
        let m = rng.below(12);
        let mut times = Vec::new();
        for _ in 0..m {
            let (u, v) = (1 + rng.below(n), 1 + rng.below(n));
            if u != v {
                times.push((u, v, rng.int(0, 9) as u32));
            }
        }
        let k = 1 + rng.below(n);
        let mut dist: Vec<Option<u32>> = vec![None; n + 1];
        dist[k] = Some(0);
        for _ in 0..n {
            for &(u, v, w) in &times {
                if let Some(d) = dist[u] {
                    if dist[v].is_none_or(|x| d + w < x) {
                        dist[v] = Some(d + w);
                    }
                }
            }
        }
        let want = dist[1..].iter().copied().collect::<Option<Vec<u32>>>().map(|d| d.into_iter().max().unwrap());
        check!(format!("times = {times:?}, n = {n}, k = {k}"), network_delay(&times, n, k), want);
    }
}

#[test]
fn scale_100k_nodes() {
    // A chain 1 → 2 → … → n listed back to front, plus 10⁵ backward edges that never help.
    let n = 100_000;
    let mut rng = anneal_prelude::Rng::new(43);
    let mut times: Vec<(usize, usize, u32)> = (1..n).rev().map(|u| (u, u + 1, 1)).collect();
    for _ in 0..100_000 {
        let (a, b) = (1 + rng.below(n), 1 + rng.below(n));
        if a != b {
            times.push((a.max(b), a.min(b), rng.int(0, 100) as u32));
        }
    }
    check!("n = 100000, chain of 1 ms edges plus 10⁵ backward edges, k = 1", network_delay(&times, n, 1), Some(99_999));
}
