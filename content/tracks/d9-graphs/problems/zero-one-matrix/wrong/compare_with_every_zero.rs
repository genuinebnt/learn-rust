pub fn update_matrix(mat: &[Vec<u8>]) -> Vec<Vec<u32>> {
    let (h, w) = (mat.len(), mat[0].len());
    let zeros: Vec<(usize, usize)> = (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).filter(|&(r, c)| mat[r][c] == 0).collect();
    (0..h).map(|r| (0..w).map(|c| zeros.iter().map(|&(a, b)| (r.abs_diff(a) + c.abs_diff(b)) as u32).min().unwrap()).collect()).collect()
}
