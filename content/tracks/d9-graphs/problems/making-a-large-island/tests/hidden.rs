use solution::*;

#[test]
fn join_four() {
    check!(r#"grid = [[0,1,0],[1,0,1],[0,1,0]]"#, largest_island(&[vec![0, 1, 0], vec![1, 0, 1], vec![0, 1, 0]]), 5);
}

#[test]
fn single_land() {
    check!(r#"grid = [[1]]"#, largest_island(&[vec![1]]), 1);
}

#[test]
fn all_water() {
    check!(r#"grid = 3×3 of 0"#, largest_island(&[vec![0, 0, 0], vec![0, 0, 0], vec![0, 0, 0]]), 1);
}

#[test]
fn one_row() {
    check!(r#"grid = [[1,1,0,1,1]]"#, largest_island(&[vec![1, 1, 0, 1, 1]]), 5);
}

#[test]
fn gap_too_wide() {
    check!(r#"grid = [[1,0,0,1]]"#, largest_island(&[vec![1, 0, 0, 1]]), 2);
}

#[test]
fn one_column() {
    check!(r#"grid = [[1],[0],[1]]"#, largest_island(&[vec![1], vec![0], vec![1]]), 3);
}

#[test]
fn u_shape_touches_twice() {
    check!(r#"grid = [[1,0,1],[1,0,1],[1,1,1]]"#, largest_island(&[vec![1, 0, 1], vec![1, 0, 1], vec![1, 1, 1]]), 8);
}

#[test]
fn corner_joins_two() {
    check!(r#"grid = [[1,1,0,1],[0,0,0,1]]"#, largest_island(&[vec![1, 1, 0, 1], vec![0, 0, 0, 1]]), 5);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(955);
    for _ in 0..300 {
        let (h, w) = (1 + rng.below(5), 1 + rng.below(5));
        let grid: Vec<Vec<u8>> = (0..h).map(|_| rng.vec(w, 0, 1)).collect();
        // Brute force: flip each 0 in turn and measure the island around it.
        let mut want = 0;
        let mut any_water = false;
        for r in 0..h {
            for c in 0..w {
                if grid[r][c] != 0 {
                    continue;
                }
                any_water = true;
                let mut g = grid.clone();
                g[r][c] = 1;
                let mut seen = vec![vec![false; w]; h];
                seen[r][c] = true;
                let mut stack = vec![(r, c)];
                let mut count = 0;
                while let Some((y, x)) = stack.pop() {
                    count += 1;
                    for (ny, nx) in [(y.wrapping_sub(1), x), (y + 1, x), (y, x.wrapping_sub(1)), (y, x + 1)] {
                        if ny < h && nx < w && g[ny][nx] == 1 && !seen[ny][nx] {
                            seen[ny][nx] = true;
                            stack.push((ny, nx));
                        }
                    }
                }
                want = want.max(count);
            }
        }
        if !any_water {
            want = h * w;
        }
        check!(format!("grid = {grid:?}"), largest_island(&grid), want);
    }
}

#[test]
fn scale_lattice_of_lakes_500() {
    // Water at every (odd row, odd column): 62500 one-cell lakes inside one island of 187500.
    let grid: Vec<Vec<u8>> = (0..500).map(|r| (0..500).map(|c| u8::from(r % 2 == 0 || c % 2 == 0)).collect()).collect();
    check!("500×500, water at every odd (row, column)", largest_island(&grid), 187_501);
}

#[test]
fn scale_two_halves_500() {
    // Column 250 is water; flipping any cell of it joins the two halves.
    let grid: Vec<Vec<u8>> = (0..500).map(|_| (0..500).map(|c| u8::from(c != 250)).collect()).collect();
    check!("500×500, all land except column 250", largest_island(&grid), 249_501);
}
