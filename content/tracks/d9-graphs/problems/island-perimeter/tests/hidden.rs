use solution::*;

#[test]
fn ring_around_a_lake() {
    check!(r#"grid = [[1,1,1],[1,0,1],[1,1,1]]"#, island_perimeter(&[vec![1, 1, 1], vec![1, 0, 1], vec![1, 1, 1]]), 16);
}

#[test]
fn row() {
    check!(r#"grid = [[1,1,1,1,1]]"#, island_perimeter(&[vec![1, 1, 1, 1, 1]]), 12);
}

#[test]
fn column() {
    check!(r#"grid = [[1],[1],[1]]"#, island_perimeter(&[vec![1], vec![1], vec![1]]), 8);
}

#[test]
fn diagonal_cells() {
    check!(r#"grid = [[1,0,1],[0,1,0],[1,0,1]]"#, island_perimeter(&[vec![1, 0, 1], vec![0, 1, 0], vec![1, 0, 1]]), 20);
}

#[test]
fn all_land_500() {
    check!(r#"500×500 all land"#, island_perimeter(&vec![vec![1; 500]; 500]), 2000);
}

#[test]
fn l_shape() {
    check!(r#"grid = [[1,0],[1,1]]"#, island_perimeter(&[vec![1, 0], vec![1, 1]]), 8);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(937);
    for _ in 0..300 {
        let (h, w) = (1 + rng.below(6), 1 + rng.below(6));
        let grid: Vec<Vec<u8>> = (0..h).map(|_| rng.vec(w, 0, 1)).collect();
        // Brute force: look at all four sides of every land cell.
        let mut want = 0;
        for r in 0..h {
            for c in 0..w {
                if grid[r][c] == 1 {
                    for (a, b) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                        if a >= h || b >= w || grid[a][b] == 0 {
                            want += 1;
                        }
                    }
                }
            }
        }
        check!(format!("grid = {grid:?}"), island_perimeter(&grid), want);
    }
}

#[test]
fn scale_snake_499x500() {
    let g: Vec<Vec<u8>> = (0..499).map(|r| if r % 2 == 0 { vec![1; 500] } else { let mut row = vec![0; 500]; row[if r % 4 == 1 { 499 } else { 0 }] = 1; row }).collect();
    check!("499×500 snake corridor", island_perimeter(&g), 250_500);
}
