use std::collections::VecDeque;

pub fn update_matrix(mat: &[Vec<u8>]) -> Vec<Vec<u32>> {
    let (h, w) = (mat.len(), mat[0].len());
    let mut dist = vec![vec![u32::MAX; w]; h];
    let mut queue = VecDeque::new();
    for r in 0..h {
        for c in 0..w {
            if mat[r][c] == 0 {
                dist[r][c] = 0;
                queue.push_back((r, c));
            }
        }
    }
    while let Some((r, c)) = queue.pop_front() {
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < h && nc < w && dist[nr][nc] == u32::MAX {
                dist[nr][nc] = dist[r][c] + 1;
                queue.push_back((nr, nc));
            }
        }
    }
    dist
}
