use solution::*;

#[test]
fn all_zero() {
    check!(r#"mat = [[0,0],[0,0]]"#, update_matrix(&[vec![0, 0], vec![0, 0]]), vec![vec![0, 0], vec![0, 0]]);
}

#[test]
fn zero_in_the_middle() {
    check!(r#"mat = [[1,1,1],[1,0,1],[1,1,1]]"#, update_matrix(&[vec![1, 1, 1], vec![1, 0, 1], vec![1, 1, 1]]), vec![vec![2, 1, 2], vec![1, 0, 1], vec![2, 1, 2]]);
}

#[test]
fn nearest_of_two() {
    check!(r#"mat = [[0,1,1,1,1,0]]"#, update_matrix(&[vec![0, 1, 1, 1, 1, 0]]), vec![vec![0, 1, 2, 2, 1, 0]]);
}

#[test]
fn column() {
    check!(r#"mat = [[1],[1],[0],[1]]"#, update_matrix(&[vec![1], vec![1], vec![0], vec![1]]), vec![vec![2], vec![1], vec![0], vec![1]]);
}

#[test]
fn far_corner_500() {
    let mut m = vec![vec![1u8; 500]; 500];
    m[0][0] = 0;
    let d = update_matrix(&m);
    check!(r#"500×500, only (0, 0) is 0"#, (d[499][499], d[0][499], d[250][250]), (998, 499, 500));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(941);
    for _ in 0..300 {
        let (h, w) = (1 + rng.below(6), 1 + rng.below(6));
        let mut mat: Vec<Vec<u8>> = (0..h).map(|_| (0..w).map(|_| u8::from(rng.below(3) > 0)).collect()).collect();
        let (zr, zc) = (rng.below(h), rng.below(w));
        mat[zr][zc] = 0;
        // Brute force: with no walls, the distance is the smallest Manhattan distance to a zero.
        let zeros: Vec<(usize, usize)> = (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).filter(|&(r, c)| mat[r][c] == 0).collect();
        let want: Vec<Vec<u32>> = (0..h).map(|r| (0..w).map(|c| zeros.iter().map(|&(a, b)| (r.abs_diff(a) + c.abs_diff(b)) as u32).min().unwrap()).collect()).collect();
        check!(format!("mat = {mat:?}"), update_matrix(&mat), want);
    }
}

#[test]
fn scale_zeros_on_top() {
    // Only the first row is 0, so a search from each cell has to walk far.
    let mut m = vec![vec![1u8; 500]; 500];
    m[0] = vec![0; 500];
    let d = update_matrix(&m);
    let total: u64 = d.iter().flatten().map(|&x| u64::from(x)).sum();
    check!("500×500, first row 0, the rest 1: sum of distances", total, 62_375_000);
}

#[test]
fn scale_checkerboard() {
    // Half the cells are 0, so comparing every cell with every zero is slow.
    let m: Vec<Vec<u8>> = (0..500).map(|r| (0..500).map(|c| u8::from((r + c) % 2 == 1)).collect()).collect();
    let d = update_matrix(&m);
    let total: u64 = d.iter().flatten().map(|&x| u64::from(x)).sum();
    check!("500×500 checkerboard: sum of distances", total, 125_000);
}
