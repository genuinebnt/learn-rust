use solution::*;

#[test]
fn one_blocked_cell() {
    check!(r#"grid = [[1]]"#, shortest_path_binary_matrix(&[vec![1]]), None);
}

#[test]
fn walled_in() {
    check!(r#"grid = [[0,1,0],[1,1,0],[0,0,0]]"#, shortest_path_binary_matrix(&[vec![0, 1, 0], vec![1, 1, 0], vec![0, 0, 0]]), None);
}

#[test]
fn straight_diagonal() {
    check!(r#"grid = [[0,1,1],[1,0,1],[1,1,0]]"#, shortest_path_binary_matrix(&[vec![0, 1, 1], vec![1, 0, 1], vec![1, 1, 0]]), Some(3));
}

#[test]
fn around_a_centre_block() {
    check!(r#"grid = [[0,0,0],[0,1,0],[0,0,0]]"#, shortest_path_binary_matrix(&[vec![0, 0, 0], vec![0, 1, 0], vec![0, 0, 0]]), Some(4));
}

#[test]
fn winding() {
    check!(r#"grid = [[0,1,0,0],[0,1,0,1],[0,0,0,1],[1,1,0,0]]"#, shortest_path_binary_matrix(&[vec![0, 1, 0, 0], vec![0, 1, 0, 1], vec![0, 0, 0, 1], vec![1, 1, 0, 0]]), Some(5));
}

#[test]
fn open_500() {
    check!(r#"500×500, all open"#, shortest_path_binary_matrix(&vec![vec![0; 500]; 500]), Some(500));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(942);
    for _ in 0..300 {
        let n = 1 + rng.below(5);
        let grid: Vec<Vec<u8>> = (0..n).map(|_| (0..n).map(|_| u8::from(rng.below(3) == 0)).collect()).collect();
        // Brute force: relax every open cell until nothing changes.
        let mut d = vec![vec![usize::MAX; n]; n];
        if grid[0][0] == 0 {
            d[0][0] = 1;
        }
        let mut changed = true;
        while changed {
            changed = false;
            for r in 0..n {
                for c in 0..n {
                    for a in r.saturating_sub(1)..=(r + 1).min(n - 1) {
                        for b in c.saturating_sub(1)..=(c + 1).min(n - 1) {
                            if grid[r][c] == 0 && d[a][b] != usize::MAX && d[a][b] + 1 < d[r][c] {
                                d[r][c] = d[a][b] + 1;
                                changed = true;
                            }
                        }
                    }
                }
            }
        }
        let want = (d[n - 1][n - 1] != usize::MAX).then_some(d[n - 1][n - 1]);
        check!(format!("grid = {grid:?}"), shortest_path_binary_matrix(&grid), want);
    }
}

#[test]
fn scale_snake_499() {
    // Open rows joined through a gap at alternating ends of each blocked row.
    let grid: Vec<Vec<u8>> = (0..499).map(|r| if r % 2 == 0 { vec![0; 499] } else { let mut row = vec![1; 499]; row[if r % 4 == 1 { 498 } else { 0 }] = 0; row }).collect();
    check!("499×499 snake", shortest_path_binary_matrix(&grid), Some(124_004));
}
