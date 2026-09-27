pub fn maximal_square(matrix: &[&str]) -> usize {
    let g: Vec<&[u8]> = matrix.iter().map(|r| r.as_bytes()).collect();
    let (m, n) = (g.len(), g.first().map_or(0, |r| r.len()));
    let mut best = 0;
    for i in 0..m {
        for j in 0..n {
            let mut k = 1;
            while i + k <= m && j + k <= n && (i..i + k).all(|r| (j..j + k).all(|c| g[r][c] == b'1')) {
                best = best.max(k);
                k += 1;
            }
        }
    }
    best * best
}
