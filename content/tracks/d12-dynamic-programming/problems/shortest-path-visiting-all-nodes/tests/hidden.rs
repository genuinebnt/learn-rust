use solution::*;

#[test]
fn empty() {
    check!(r#"graph = []"#, shortest_path_length(&[]), 0);
}

#[test]
fn single_node() {
    check!(r#"graph = [[]]"#, shortest_path_length(&[vec![]]), 0);
}

#[test]
fn lollipop() {
    let g = vec![vec![1, 2], vec![0, 2], vec![1, 0, 3], vec![2, 4], vec![3, 5], vec![4]];
    check!(r#"a triangle 0-1-2 with a tail 2-3-4-5"#, shortest_path_length(&g), 5);
}

#[test]
fn spider() {
    let g = vec![vec![1, 4, 7], vec![0, 2], vec![1, 3], vec![2], vec![0, 5], vec![4, 6], vec![5], vec![0, 8], vec![7, 9], vec![8]];
    check!(r#"node 0 with three legs of three nodes each"#, shortest_path_length(&g), 12);
}

#[test]
fn path_12() {
    let g: Vec<Vec<usize>> = (0..12usize).map(|i| [i.checked_sub(1), (i + 1 < 12).then_some(i + 1)].into_iter().flatten().collect()).collect();
    check!(r#"a path 0-1-…-11"#, shortest_path_length(&g), 11);
}

#[test]
fn star_12() {
    let g: Vec<Vec<usize>> = (0..12).map(|i| if i == 0 { (1..12).collect() } else { vec![0] }).collect();
    check!(r#"node 0 joined to nodes 1..=11"#, shortest_path_length(&g), 20);
}

#[test]
fn complete_12() {
    let g: Vec<Vec<usize>> = (0..12).map(|i| (0..12).filter(|&j| j != i).collect()).collect();
    check!(r#"every pair of 12 nodes joined"#, shortest_path_length(&g), 11);
}

#[test]
fn binary_tree_12() {
    let mut g = vec![vec![]; 12];
    for i in 1..12usize {
        g[i].push((i - 1) / 2);
        g[(i - 1) / 2].push(i);
    }
    check!(r#"node i > 0 joined to (i - 1) / 2, 12 nodes"#, shortest_path_length(&g), 16);
}

#[test]
fn random_vs_brute_force() {
    // Shortest distances between all pairs, then the best order to visit the nodes in.
    fn best(dist: &[Vec<usize>], order: &mut Vec<usize>, used: &mut Vec<bool>) -> usize {
        let n = dist.len();
        if order.len() == n {
            return order.windows(2).map(|w| dist[w[0]][w[1]]).sum();
        }
        let mut top = usize::MAX;
        for v in 0..n {
            if !used[v] {
                used[v] = true;
                order.push(v);
                top = top.min(best(dist, order, used));
                order.pop();
                used[v] = false;
            }
        }
        top
    }
    let mut rng = anneal_prelude::Rng::new(1249);
    for _ in 0..300 {
        let n = rng.int(1, 7) as usize;
        let mut g = vec![vec![]; n];
        // A random tree keeps it connected, then a few extra edges.
        for v in 1..n {
            let u = rng.below(v);
            g[u].push(v);
            g[v].push(u);
        }
        let extra = rng.below(n + 1);
        for _ in 0..extra {
            let (a, b) = (rng.below(n), rng.below(n));
            if a != b && !g[a].contains(&b) {
                g[a].push(b);
                g[b].push(a);
            }
        }
        let mut dist = vec![vec![usize::MAX / 4; n]; n];
        for u in 0..n {
            dist[u][u] = 0;
            for &v in &g[u] {
                dist[u][v] = 1;
            }
        }
        for k in 0..n {
            for i in 0..n {
                for j in 0..n {
                    dist[i][j] = dist[i][j].min(dist[i][k] + dist[k][j]);
                }
            }
        }
        let want = best(&dist, &mut vec![], &mut vec![false; n]);
        check!(format!("graph = {g:?}"), shortest_path_length(&g), want);
    }
}

#[test]
fn scale_twelve_nodes() {
    // A cycle of 12 with a few chords; brute force over visiting orders is 12! ≈ 4.8·10⁸.
    let mut g: Vec<Vec<usize>> = (0..12).map(|i| vec![(i + 11) % 12, (i + 1) % 12]).collect();
    for (a, b) in [(0, 6), (3, 9), (1, 7)] {
        g[a].push(b);
        g[b].push(a);
    }
    check!("cycle of 12 plus chords 0-6, 3-9, 1-7", shortest_path_length(&g), 11);
    let star: Vec<Vec<usize>> = (0..12).map(|i| if i == 0 { (1..12).collect() } else { vec![0] }).collect();
    check!("star of 12", shortest_path_length(&star), 20);
}
