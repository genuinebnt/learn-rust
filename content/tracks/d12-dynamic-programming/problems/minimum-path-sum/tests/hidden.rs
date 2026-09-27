use solution::*;

#[test]
fn one_cell() {
    check!(r#"grid = [[0]]"#, min_path_sum(&[vec![0]]), 0);
}

#[test]
fn zeros() {
    check!(r#"grid = [[0, 0], [0, 0]]"#, min_path_sum(&[vec![0, 0], vec![0, 0]]), 0);
}

#[test]
fn tie() {
    check!(r#"grid = [[1, 2], [1, 1]]"#, min_path_sum(&[vec![1, 2], vec![1, 1]]), 3);
}

#[test]
fn winding() {
    check!(r#"grid = [[1, 1, 9, 9], [5, 1, 9, 9], [5, 9, 9, 9], [1, 1, 1, 1]]"#, min_path_sum(&[vec![1, 1, 9, 9], vec![5, 1, 9, 9], vec![5, 9, 9, 9], vec![1, 1, 1, 1]]), 15);
}

#[test]
fn greedy_trap() {
    check!(r#"grid = 7 × 8 (LeetCode)"#, min_path_sum(&[vec![1, 4, 8, 6, 2, 2, 1, 7], vec![4, 7, 3, 1, 4, 5, 5, 1], vec![8, 8, 2, 1, 1, 8, 0, 1], vec![8, 9, 2, 9, 8, 0, 8, 9], vec![5, 7, 5, 7, 1, 8, 5, 5], vec![7, 0, 9, 4, 5, 6, 5, 6], vec![4, 9, 9, 7, 9, 1, 9, 0]]), 47);
}

#[test]
fn long_row() {
    check!(r#"grid = [[10000; 1000]]"#, min_path_sum(&[vec![10_000; 1000]]), 10_000_000);
}

#[test]
fn past_u32() {
    check!(r#"grid = 1000 × 1000 of 10000"#, min_path_sum(&vec![vec![10_000; 1000]; 1000]), 19_990_000);
}

#[test]
fn random_vs_brute_force() {
    fn cheapest(g: &[Vec<u32>], i: usize, j: usize) -> u64 {
        let here = g[i][j] as u64;
        match (i, j) {
            (0, 0) => here,
            (0, _) => here + cheapest(g, 0, j - 1),
            (_, 0) => here + cheapest(g, i - 1, 0),
            _ => here + cheapest(g, i - 1, j).min(cheapest(g, i, j - 1)),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1220);
    for _ in 0..300 {
        let m = rng.int(1, 6) as usize;
        let n = rng.int(1, 6) as usize;
        let grid: Vec<Vec<u32>> = (0..m).map(|_| rng.vec(n, 0, 9)).collect();
        check!(format!("grid = {grid:?}"), min_path_sum(&grid), cheapest(&grid, m - 1, n - 1));
    }
}

#[test]
fn scale_1000() {
    let grid: Vec<Vec<u32>> = (0..1000u32).map(|i| (0..1000u32).map(|j| (i * 31 + j * 17) % 100).collect()).collect();
    check!("grid[i][j] = (31i + 17j) % 100, 1000 × 1000", min_path_sum(&grid), 72_771);
}
