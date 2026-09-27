use solution::*;

#[test]
fn one_blocked_cell() {
    check!(r#"grid = [[1]]"#, unique_paths_with_obstacles(&[vec![1]]), 0);
}

#[test]
fn start_blocked() {
    check!(r#"grid = [[1, 0], [0, 0]]"#, unique_paths_with_obstacles(&[vec![1, 0], vec![0, 0]]), 0);
}

#[test]
fn first_row_cut_off() {
    check!(r#"grid = [[0, 1, 0], [0, 0, 0]]"#, unique_paths_with_obstacles(&[vec![0, 1, 0], vec![0, 0, 0]]), 1);
}

#[test]
fn wall() {
    check!(r#"grid = [[0, 0], [1, 1], [0, 0]]"#, unique_paths_with_obstacles(&[vec![0, 0], vec![1, 1], vec![0, 0]]), 0);
}

#[test]
fn single_row_blocked() {
    check!(r#"grid = [[0, 0, 1, 0]]"#, unique_paths_with_obstacles(&[vec![0, 0, 1, 0]]), 0);
}

#[test]
fn single_column() {
    check!(r#"grid = [[0], [0], [0]]"#, unique_paths_with_obstacles(&[vec![0], vec![0], vec![0]]), 1);
}

#[test]
fn single_column_blocked() {
    check!(r#"grid = [[0], [1], [0]]"#, unique_paths_with_obstacles(&[vec![0], vec![1], vec![0]]), 0);
}

#[test]
fn scattered() {
    check!(r#"grid = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0]]"#, unique_paths_with_obstacles(&[vec![0, 0, 0, 0], vec![0, 1, 0, 0], vec![0, 0, 0, 1], vec![1, 0, 0, 0]]), 3);
}

#[test]
fn random_vs_brute_force() {
    fn count(g: &[Vec<u8>], i: usize, j: usize) -> u64 {
        if g[i][j] == 1 {
            return 0;
        }
        if i == 0 && j == 0 {
            return 1;
        }
        (if i > 0 { count(g, i - 1, j) } else { 0 }) + (if j > 0 { count(g, i, j - 1) } else { 0 })
    }
    let mut rng = anneal_prelude::Rng::new(1219);
    for _ in 0..300 {
        let m = rng.int(1, 7) as usize;
        let n = rng.int(1, 7) as usize;
        let grid: Vec<Vec<u8>> = (0..m).map(|_| (0..n).map(|_| (rng.below(4) == 0) as u8).collect()).collect();
        check!(format!("grid = {grid:?}"), unique_paths_with_obstacles(&grid), count(&grid, m - 1, n - 1));
    }
}

#[test]
fn scale_free_33() {
    let grid = vec![vec![0u8; 33]; 33];
    check!("grid = 33 × 33, no obstacles", unique_paths_with_obstacles(&grid), 1_832_624_140_942_590_534);
}

#[test]
fn scale_rocks_33() {
    let grid: Vec<Vec<u8>> = (0..33usize)
        .map(|i| (0..33usize).map(|j| ((i * 7 + j * 3) % 11 == 5 && (i, j) != (0, 0) && (i, j) != (32, 32)) as u8).collect())
        .collect();
    check!("grid = 33 × 33, rock where (7i + 3j) % 11 == 5", unique_paths_with_obstacles(&grid), 105_440_613_552_200);
}
