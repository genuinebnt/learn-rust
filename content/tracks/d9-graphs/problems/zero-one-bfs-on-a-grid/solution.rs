use std::collections::VecDeque;

pub fn min_walls(grid: &[&str]) -> u32 {
    let g: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
    let (h, w) = (g.len(), g[0].len());
    let mut dist = vec![vec![u32::MAX; w]; h];
    dist[0][0] = 0;
    let mut deque = VecDeque::from([(0usize, 0usize)]);
    while let Some((r, c)) = deque.pop_front() {
        let d = dist[r][c];
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr >= h || nc >= w {
                continue;
            }
            let cost = u32::from(g[nr][nc] == b'#');
            if d + cost < dist[nr][nc] {
                dist[nr][nc] = d + cost;
                if cost == 0 {
                    deque.push_front((nr, nc));
                } else {
                    deque.push_back((nr, nc));
                }
            }
        }
    }
    dist[h - 1][w - 1]
}
