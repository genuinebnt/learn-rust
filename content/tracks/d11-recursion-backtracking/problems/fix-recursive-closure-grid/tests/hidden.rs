use solution::*;

#[test]
fn single_cell() {
    check!(r#"grid = [[1]]"#, island_sizes(vec![vec![1]]), vec![1]);
}

#[test]
fn u_shape() {
    check!(r#"grid = [[1, 0, 1], [1, 0, 1], [1, 1, 1]]"#, island_sizes(vec![vec![1, 0, 1], vec![1, 0, 1], vec![1, 1, 1]]), vec![7]);
}

#[test]
fn ring_around_a_dot() {
    check!(r#"grid = 5×5 ring of 1s with a 1 in the middle"#, island_sizes(vec![vec![1, 1, 1, 1, 1], vec![1, 0, 0, 0, 1], vec![1, 0, 1, 0, 1], vec![1, 0, 0, 0, 1], vec![1, 1, 1, 1, 1]]), vec![16, 1]);
}

#[test]
fn single_row() {
    check!(r#"grid = [[1, 1, 0, 1, 0, 1, 1, 1]]"#, island_sizes(vec![vec![1, 1, 0, 1, 0, 1, 1, 1]]), vec![2, 1, 3]);
}

#[test]
fn single_column() {
    check!(r#"grid = [[1], [0], [1], [1]]"#, island_sizes(vec![vec![1], vec![0], vec![1], vec![1]]), vec![1, 2]);
}

#[test]
fn rows_of_nothing() {
    check!(r#"grid = [[], []]"#, island_sizes(vec![vec![], vec![]]), Vec::<usize>::new());
}

#[test]
fn reaches_back_up() {
    check!(r#"grid = [[0, 1], [0, 1], [1, 1]]: the island's first cell is (0, 1)"#, island_sizes(vec![vec![0, 1], vec![0, 1], vec![1, 1]]), vec![4]);
}

#[test]
fn full_50x50() {
    check!(r#"grid = 50×50 of 1"#, island_sizes(vec![vec![1; 50]; 50]), vec![2500]);
}

#[test]
fn checkerboard_50x50() {
    check!(r#"grid = 50×50 checkerboard"#, island_sizes((0..50).map(|r| (0..50).map(|c| ((r + c) % 2 == 0) as u8).collect()).collect()), vec![1; 1250]);
}

#[test]
fn random_vs_breadth_first_labels() {
    let mut rng = anneal_prelude::Rng::new(1132);
    for _ in 0..300 {
        let (h, w) = (rng.int(1, 8) as usize, rng.int(1, 8) as usize);
        let grid: Vec<Vec<u8>> = (0..h).map(|_| rng.vec(w, 0, 1)).collect();
        let mut seen = vec![vec![false; w]; h];
        let mut want = Vec::new();
        for r in 0..h {
            for c in 0..w {
                if grid[r][c] == 1 && !seen[r][c] {
                    seen[r][c] = true;
                    let mut queue = std::collections::VecDeque::from([(r, c)]);
                    let mut size = 0;
                    while let Some((a, b)) = queue.pop_front() {
                        size += 1;
                        for (x, y) in [(a.wrapping_sub(1), b), (a + 1, b), (a, b.wrapping_sub(1)), (a, b + 1)] {
                            if x < h && y < w && grid[x][y] == 1 && !seen[x][y] {
                                seen[x][y] = true;
                                queue.push_back((x, y));
                            }
                        }
                    }
                    want.push(size);
                }
            }
        }
        check!(format!("grid = {grid:?}"), island_sizes(grid.clone()), want);
    }
}

#[test]
fn scale_snake_50x50() {
    // Rows of land joined at alternating ends: one island of 1275 cells, 1275 calls deep.
    let grid: Vec<Vec<u8>> = (0..50)
        .map(|r| (0..50).map(|c| if r % 2 == 0 || (r % 4 == 1 && c == 49) || (r % 4 == 3 && c == 0) { 1 } else { 0 }).collect())
        .collect();
    check!("grid = 50×50 snake", island_sizes(grid), vec![1275]);
}
