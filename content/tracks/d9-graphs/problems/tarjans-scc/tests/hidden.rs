use solution::*;

#[test]
fn self_loop() {
    check!(r#"adj = [[0]]"#, strongly_connected(&[vec![0]]), vec![vec![0]]);
}

#[test]
fn back_to_earlier_scc() {
    check!(r#"adj = [[1], [0], [0, 3], [2]]"#, strongly_connected(&[vec![1], vec![0], vec![0, 3], vec![2]]), vec![vec![0, 1], vec![2, 3]]);
}

#[test]
fn big_cycle() {
    let adj: Vec<Vec<usize>> = (0..5000).map(|i| vec![(i + 1) % 5000]).collect();
    let out = strongly_connected(&adj);
    check!(r#"one cycle of 5000 nodes"#, (out.len(), out[0].len()), (1, 5000));
}

#[test]
fn empty_graph() {
    check!(r#"adj = []"#, strongly_connected(&[]), Vec::<Vec<usize>>::new());
}

#[test]
fn cross_edge_to_a_finished_component() {
    check!(r#"adj = [[1, 2], [], [1]]"#, strongly_connected(&[vec![1, 2], vec![], vec![1]]), vec![vec![0], vec![1], vec![2]]);
}

#[test]
fn repeated_edges() {
    check!(r#"adj = [[1, 1], [0, 0, 2], [2]]"#, strongly_connected(&[vec![1, 1], vec![0, 0, 2], vec![2]]), vec![vec![0, 1], vec![2]]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(927);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let adj: Vec<Vec<usize>> = (0..n).map(|_| { let k = rng.below(3); (0..k).map(|_| rng.below(n)).collect() }).collect();
        // Brute force: transitive closure, then group nodes that reach each other.
        let mut reach = vec![vec![false; n]; n];
        for u in 0..n {
            reach[u][u] = true;
            for &v in &adj[u] {
                reach[u][v] = true;
            }
        }
        for k in 0..n {
            for i in 0..n {
                for j in 0..n {
                    if reach[i][k] && reach[k][j] {
                        reach[i][j] = true;
                    }
                }
            }
        }
        let mut want: Vec<Vec<usize>> = Vec::new();
        for u in 0..n {
            if (0..u).all(|v| !(reach[u][v] && reach[v][u])) {
                want.push((u..n).filter(|&v| reach[u][v] && reach[v][u]).collect());
            }
        }
        check!(format!("adj = {adj:?}"), strongly_connected(&adj), want);
    }
}

#[test]
fn chain_of_pairs_5000() {
    // 2i ↔ 2i+1, and 2i+1 → 2i+2: 2500 components of two.
    let adj: Vec<Vec<usize>> = (0..5000).map(|u| if u % 2 == 0 { vec![u + 1] } else if u + 1 < 5000 { vec![u - 1, u + 1] } else { vec![u - 1] }).collect();
    let out = strongly_connected(&adj);
    check!("2500 two-cycles joined in a chain", (out.len(), out[0].clone(), out[2499].clone()), (2500, vec![0, 1], vec![4998, 4999]));
}
