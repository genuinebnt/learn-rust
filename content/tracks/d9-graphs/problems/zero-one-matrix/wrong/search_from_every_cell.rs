use std::collections::VecDeque;

pub fn update_matrix(mat: &[Vec<u8>]) -> Vec<Vec<u32>> {
    let (h, w) = (mat.len(), mat[0].len());
    let mut out = vec![vec![0; w]; h];
    for r0 in 0..h {
        for c0 in 0..w {
            let mut seen = vec![vec![false; w]; h];
            seen[r0][c0] = true;
            let mut queue = VecDeque::from([(r0, c0, 0u32)]);
            while let Some((r, c, d)) = queue.pop_front() {
                if mat[r][c] == 0 {
                    out[r0][c0] = d;
                    break;
                }
                for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if nr < h && nc < w && !seen[nr][nc] {
                        seen[nr][nc] = true;
                        queue.push_back((nr, nc, d + 1));
                    }
                }
            }
        }
    }
    out
}
