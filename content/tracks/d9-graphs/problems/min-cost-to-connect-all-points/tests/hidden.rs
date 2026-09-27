use solution::*;

#[test]
fn star_beats_path() {
    check!(r#"points = [(0,0), (1,0), (-1,0), (0,1), (0,-1)]"#, min_cost_connect_points(&[(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]), 4);
}

#[test]
fn far_corners() {
    check!(r#"points = [(-10⁶,-10⁶), (10⁶,10⁶), (-10⁶,10⁶), (10⁶,-10⁶)]"#, min_cost_connect_points(&[(-1_000_000, -1_000_000), (1_000_000, 1_000_000), (-1_000_000, 1_000_000), (1_000_000, -1_000_000)]), 6_000_000);
}

#[test]
fn collinear() {
    check!(r#"points = [(0,5), (0,1), (0,3), (0,2)]"#, min_cost_connect_points(&[(0, 5), (0, 1), (0, 3), (0, 2)]), 4);
}

#[test]
fn two_clusters() {
    check!(r#"points = [(0,0), (1,1), (100,100), (101,100)]"#, min_cost_connect_points(&[(0, 0), (1, 1), (100, 100), (101, 100)]), 201);
}

#[test]
fn diagonal_neighbours() {
    check!(r#"points = [(0,0), (1,1), (2,2), (3,3)]"#, min_cost_connect_points(&[(0, 0), (1, 1), (2, 2), (3, 3)]), 6);
}

#[test]
fn cheapest_link_found_late() {
    check!(r#"points = [(0,0), (5,0), (5,1), (0,6)]"#, min_cost_connect_points(&[(0, 0), (5, 0), (5, 1), (0, 6)]), 12);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(952);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let mut points: Vec<(i32, i32)> = Vec::new();
        while points.len() < n {
            let p = (rng.int(-6, 6) as i32, rng.int(-6, 6) as i32);
            if !points.contains(&p) {
                points.push(p);
            }
        }
        // Brute force: Kruskal over every pair.
        let mut edges: Vec<(u64, usize, usize)> = Vec::new();
        for a in 0..n {
            for b in a + 1..n {
                edges.push((((points[a].0 - points[b].0).abs() + (points[a].1 - points[b].1).abs()) as u64, a, b));
            }
        }
        edges.sort();
        let mut comp: Vec<usize> = (0..n).collect();
        let mut want = 0;
        for (w, a, b) in edges {
            let (ca, cb) = (comp[a], comp[b]);
            if ca != cb {
                want += w;
                for c in comp.iter_mut() {
                    if *c == cb {
                        *c = ca;
                    }
                }
            }
        }
        check!(format!("points = {points:?}"), min_cost_connect_points(&points), want);
    }
}

#[test]
fn scale_3000_points() {
    // 3000 distinct pseudo-random points in [-10⁶, 10⁶]² (LCG seed 11).
    let mut x: u64 = 11;
    let mut next = || { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); x >> 33 };
    let mut points: Vec<(i32, i32)> = Vec::new();
    for _ in 0..3000 {
        let a = (next() % 2_000_001) as i32 - 1_000_000;
        let b = (next() % 2_000_001) as i32 - 1_000_000;
        points.push((a, b));
    }
    check!("3000 pseudo-random points", min_cost_connect_points(&points), 89_732_897);
}
