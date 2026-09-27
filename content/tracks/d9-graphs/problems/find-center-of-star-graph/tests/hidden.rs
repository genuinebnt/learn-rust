use solution::*;

#[test]
fn center_always_first() {
    check!(r#"edges = [(5, 1), (5, 2), (5, 3)]"#, find_center(&[(5, 1), (5, 2), (5, 3)]), 5);
}

#[test]
fn first_edge_reversed() {
    check!(r#"edges = [(2, 8), (8, 3)]"#, find_center(&[(2, 8), (8, 3)]), 8);
}

#[test]
fn second_edge_reversed() {
    check!(r#"edges = [(8, 2), (3, 8)]"#, find_center(&[(8, 2), (3, 8)]), 8);
}

#[test]
fn largest_label() {
    check!(r#"edges = [(u32::MAX, 0), (1, u32::MAX)]"#, find_center(&[(u32::MAX, 0), (1, u32::MAX)]), u32::MAX);
}

#[test]
fn label_zero() {
    check!(r#"edges = [(4, 0), (0, 6)]"#, find_center(&[(4, 0), (0, 6)]), 0);
}

#[test]
fn big_star() {
    let edges: Vec<(u32, u32)> = (1..=100_000u32).filter(|&v| v != 50_000).map(|v| if v % 2 == 0 { (v, 50_000) } else { (50_000, v) }).collect();
    check!(r#"center 50000 joined to 1..=100000 except itself"#, find_center(&edges), 50_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(934);
    for _ in 0..300 {
        let n = 3 + rng.below(8);
        let mut labels: Vec<u32> = (1..=20).collect();
        rng.shuffle(&mut labels);
        let center = labels[0];
        let mut edges: Vec<(u32, u32)> = labels[1..n].iter().map(|&v| if rng.bool() { (center, v) } else { (v, center) }).collect();
        rng.shuffle(&mut edges);
        // Brute force: the label that appears in every edge.
        let want = labels[..n].iter().copied().find(|&x| edges.iter().all(|&(a, b)| a == x || b == x)).unwrap();
        check!(format!("edges = {edges:?}"), find_center(&edges), want);
    }
}

#[test]
fn three_node_orientations() {
    // Every orientation and order of a 3-node star centred on 2.
    let mut bad = Vec::new();
    for e0 in [(1, 2), (2, 1)] {
        for e1 in [(3, 2), (2, 3)] {
            for edges in [[e0, e1], [e1, e0]] {
                if find_center(&edges) != 2 {
                    bad.push(edges);
                }
            }
        }
    }
    check!("all 8 ways to write a star 1-2-3", bad, Vec::<[(u32, u32); 2]>::new());
}
