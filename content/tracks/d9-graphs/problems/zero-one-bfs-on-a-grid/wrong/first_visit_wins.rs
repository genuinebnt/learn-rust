use std::collections::VecDeque;

pub fn min_walls(grid: &[&str]) -> u32 {
    let g: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
    let (h, w) = (g.len(), g[0].len());
    let mut dist = vec![vec![u32::MAX; w]; h];
    dist[0][0] = 0;
    let mut queue = VecDeque::from([(0usize, 0usize)]);
    while let Some((r, c)) = queue.pop_front() {
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < h && nc < w && dist[nr][nc] == u32::MAX {
                dist[nr][nc] = dist[r][c] + u32::from(g[nr][nc] == b'#');
                queue.push_back((nr, nc));
            }
        }
    }
    dist[h - 1][w - 1]
}
