use solution::*;

#[test]
fn go_around_the_peak() {
    check!(r#"grid = [[5,4,3],[6,7,2],[9,8,1]]"#, swim_in_water(&[vec![5, 4, 3], vec![6, 7, 2], vec![9, 8, 1]]), 5);
}

#[test]
fn single_high_cell() {
    check!(r#"grid = [[1000000000]]"#, swim_in_water(&[vec![1_000_000_000]]), 1_000_000_000);
}

#[test]
fn flat() {
    check!(r#"grid = [[7,7],[7,7]]"#, swim_in_water(&[vec![7, 7], vec![7, 7]]), 7);
}

#[test]
fn detour_below_the_wall() {
    check!(r#"grid = [[0,8,1],[1,8,1],[1,1,1]]"#, swim_in_water(&[vec![0, 8, 1], vec![1, 8, 1], vec![1, 1, 1]]), 1);
}

#[test]
fn row_major_ramp() {
    check!(r#"grid[r][c] = 3r + c on 3×3"#, swim_in_water(&[vec![0, 1, 2], vec![3, 4, 5], vec![6, 7, 8]]), 8);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(950);
    for _ in 0..300 {
        let n = 1 + rng.below(5);
        let grid: Vec<Vec<u32>> = (0..n).map(|_| rng.vec(n, 0, 20)).collect();
        // Brute force: the first water level at which a flood fill from the start reaches the end.
        let mut want = 0;
        loop {
            let mut seen = vec![vec![false; n]; n];
            let mut stack = Vec::new();
            if grid[0][0] <= want {
                seen[0][0] = true;
                stack.push((0usize, 0usize));
            }
            while let Some((r, c)) = stack.pop() {
                for (a, b) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if a < n && b < n && !seen[a][b] && grid[a][b] <= want {
                        seen[a][b] = true;
                        stack.push((a, b));
                    }
                }
            }
            if seen[n - 1][n - 1] {
                break;
            }
            want += 1;
        }
        check!(format!("grid = {grid:?}"), swim_in_water(&grid), want);
    }
}

#[test]
fn scale_ramp_300() {
    // Heights rise row by row, so every level up to the last matters.
    let n = 300;
    let grid: Vec<Vec<u32>> = (0..n).map(|r| (0..n).map(|c| (r * n + c) as u32).collect()).collect();
    check!("300×300, grid[r][c] = 300r + c", swim_in_water(&grid), 89_999);
}

#[test]
fn scale_high_wall() {
    // A full row of very high cells across the middle; the lowest of them is the answer.
    let n = 300;
    let grid: Vec<Vec<u32>> = (0..n).map(|r| (0..n).map(|c| if r == 150 { (n * n + c) as u32 } else { ((r * n + c) % 1000) as u32 }).collect()).collect();
    check!("300×300 with a wall of heights 90000.. in row 150", swim_in_water(&grid), 90_000);
}
