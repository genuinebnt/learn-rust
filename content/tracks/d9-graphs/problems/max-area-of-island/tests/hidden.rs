use solution::*;

#[test]
fn ring() {
    check!(r#"grid = [[1,1,1],[1,0,1],[1,1,1]]"#, max_area_of_island(&[vec![1, 1, 1], vec![1, 0, 1], vec![1, 1, 1]]), 8);
}

#[test]
fn checkerboard() {
    check!(r#"grid = [[1,0,1],[0,1,0],[1,0,1]]"#, max_area_of_island(&[vec![1, 0, 1], vec![0, 1, 0], vec![1, 0, 1]]), 1);
}

#[test]
fn equal_islands() {
    check!(r#"grid = [[1,1,0,1,1]]"#, max_area_of_island(&[vec![1, 1, 0, 1, 1]]), 2);
}

#[test]
fn u_shape() {
    check!(r#"grid = [[1,0,1],[1,0,1],[1,1,1]]"#, max_area_of_island(&[vec![1, 0, 1], vec![1, 0, 1], vec![1, 1, 1]]), 7);
}

#[test]
fn touching_only_at_a_corner() {
    check!(r#"grid = [[1,1,0],[0,0,1],[0,1,1]]"#, max_area_of_island(&[vec![1, 1, 0], vec![0, 0, 1], vec![0, 1, 1]]), 3);
}

#[test]
fn all_land_500() {
    check!(r#"500×500 all land"#, max_area_of_island(&vec![vec![1; 500]; 500]), 250_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(938);
    for _ in 0..300 {
        let (h, w) = (1 + rng.below(6), 1 + rng.below(6));
        let grid: Vec<Vec<u8>> = (0..h).map(|_| rng.vec(w, 0, 1)).collect();
        // Brute force: label propagation, then the most common label among land cells.
        let mut label: Vec<Vec<usize>> = (0..h).map(|r| (0..w).map(|c| r * w + c).collect()).collect();
        let mut changed = true;
        while changed {
            changed = false;
            for r in 0..h {
                for c in 0..w {
                    for (a, b) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                        if grid[r][c] == 1 && a < h && b < w && grid[a][b] == 1 && label[a][b] < label[r][c] {
                            label[r][c] = label[a][b];
                            changed = true;
                        }
                    }
                }
            }
        }
        let want = (0..h * w).map(|l| (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).filter(|&(r, c)| grid[r][c] == 1 && label[r][c] == l).count()).max().unwrap_or(0);
        check!(format!("grid = {grid:?}"), max_area_of_island(&grid), want);
    }
}

#[test]
fn scale_snake_499x500() {
    let g: Vec<Vec<u8>> = (0..499).map(|r| if r % 2 == 0 { vec![1; 500] } else { let mut row = vec![0; 500]; row[if r % 4 == 1 { 499 } else { 0 }] = 1; row }).collect();
    check!("499×500 snake corridor", max_area_of_island(&g), 125_249);
}
