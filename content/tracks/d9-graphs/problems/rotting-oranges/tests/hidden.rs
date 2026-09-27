use solution::*;

#[test]
fn nothing_fresh() {
    check!(r#"grid = [[0,2]]"#, minutes_to_rot(&[vec![0, 2]]), Some(0));
}

#[test]
fn no_rotten() {
    check!(r#"grid = [[1]]"#, minutes_to_rot(&[vec![1]]), None);
}

#[test]
fn two_sources() {
    check!(r#"grid = [[2,1,1,1,2]]"#, minutes_to_rot(&[vec![2, 1, 1, 1, 2]]), Some(2));
}

#[test]
fn single_rotten() {
    check!(r#"grid = [[2]]"#, minutes_to_rot(&[vec![2]]), Some(0));
}

#[test]
fn all_empty() {
    check!(r#"grid = [[0,0],[0,0]]"#, minutes_to_rot(&[vec![0, 0], vec![0, 0]]), Some(0));
}

#[test]
fn walled_off() {
    check!(r#"grid = [[2,0,1]]"#, minutes_to_rot(&[vec![2, 0, 1]]), None);
}

#[test]
fn column() {
    check!(r#"grid = [[2],[1],[1],[1]]"#, minutes_to_rot(&[vec![2], vec![1], vec![1], vec![1]]), Some(3));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(908);
    for _ in 0..300 {
        let h = 1 + rng.below(5);
        let w = 1 + rng.below(5);
        let grid: Vec<Vec<u8>> = (0..h).map(|_| rng.vec(w, 0, 2)).collect();
        // Brute force: simulate minute by minute.
        let mut g = grid.clone();
        let mut minutes = 0;
        let want = loop {
            let fresh = g.iter().flatten().filter(|&&x| x == 1).count();
            if fresh == 0 {
                break Some(minutes);
            }
            let prev = g.clone();
            for r in 0..h {
                for c in 0..w {
                    let near = [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)];
                    if prev[r][c] == 1 && near.iter().any(|&(nr, nc)| nr < h && nc < w && prev[nr][nc] == 2) {
                        g[r][c] = 2;
                    }
                }
            }
            if g == prev {
                break None;
            }
            minutes += 1;
        };
        check!(format!("grid = {grid:?}"), minutes_to_rot(&grid), want);
    }
}

#[test]
fn scale_snake_499x500() {
    // Full rows joined at alternating ends: one corridor 125249 cells long, rotten at its start.
    let mut grid: Vec<Vec<u8>> = (0..499)
        .map(|r| if r % 2 == 0 { vec![1; 500] } else { let mut row = vec![0; 500]; row[if r % 4 == 1 { 499 } else { 0 }] = 1; row })
        .collect();
    grid[0][0] = 2;
    check!("499×500 snake corridor, rotten at (0, 0)", minutes_to_rot(&grid), Some(125_248));
}
