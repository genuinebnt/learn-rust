use solution::*;

#[test]
fn pairs_joined_later() {
    check!(r#"n = 6, edges = [(0,1), (2,3), (4,5), (1,2)]"#, count_components(6, &[(0, 1), (2, 3), (4, 5), (1, 2)]), 2);
}

#[test]
fn self_loop() {
    check!(r#"n = 3, edges = [(0,0), (1,2), (2,1)]"#, count_components(3, &[(0, 0), (1, 2), (2, 1)]), 2);
}

#[test]
fn star() {
    check!(r#"n = 6, edges = [(0,1), (0,2), (0,3), (0,4), (0,5)]"#, count_components(6, &[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]), 1);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(923);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let m = rng.below(10);
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        // Brute force: label propagation.
        let mut label: Vec<usize> = (0..n).collect();
        loop {
            let mut changed = false;
            for &(a, b) in &edges {
                let low = label[a].min(label[b]);
                if label[a] != low || label[b] != low {
                    label[a] = low;
                    label[b] = low;
                    changed = true;
                }
            }
            if !changed {
                break;
            }
        }
        let want = (0..n).filter(|&u| label[u] == u).count();
        check!(format!("n = {n}, edges = {edges:?}"), count_components(n, &edges), want);
    }
}

#[test]
fn scale_star_200k() {
    let n = 200_000;
    let edges: Vec<(usize, usize)> = (1..n).map(|i| (0, i)).collect();
    check!("n = 200000, 0 joined to every other node", count_components(n, &edges), 1);
}

#[test]
fn isolated() {
    check!(r#"n = 3, edges = []"#, count_components(3, &[]), 3);
}

#[test]
fn million() {
    let edges: Vec<(usize, usize)> = (0..500_000).map(|i| (2 * i, 2 * i + 1)).collect();
    check!(r#"n = 10⁶, edges pair up neighbours (0-1, 2-3, …)"#, count_components(1_000_000, &edges), 500_000);
}

#[test]
fn long_chain() {
    let edges: Vec<(usize, usize)> = (1..1_000_000).map(|i| (i, i - 1)).collect();
    check!(r#"n = 10⁶, chain"#, count_components(1_000_000, &edges), 1);
}
