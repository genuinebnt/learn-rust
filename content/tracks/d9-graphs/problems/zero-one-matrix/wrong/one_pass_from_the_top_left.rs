pub fn update_matrix(mat: &[Vec<u8>]) -> Vec<Vec<u32>> {
    let (h, w) = (mat.len(), mat[0].len());
    let mut d = vec![vec![u32::MAX / 2; w]; h];
    for r in 0..h {
        for c in 0..w {
            if mat[r][c] == 0 {
                d[r][c] = 0;
            } else {
                if r > 0 {
                    d[r][c] = d[r][c].min(d[r - 1][c] + 1);
                }
                if c > 0 {
                    d[r][c] = d[r][c].min(d[r][c - 1] + 1);
                }
            }
        }
    }
    d
}
