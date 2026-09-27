pub fn min_walls(grid: &[&str]) -> u32 {
    let g: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
    let (h, w) = (g.len(), g[0].len());
    let mut dist = vec![vec![u32::MAX; w]; h];
    dist[0][0] = 0;
    let mut changed = true;
    while changed {
        changed = false;
        for r in 0..h {
            for c in 0..w {
                if dist[r][c] == u32::MAX {
                    continue;
                }
                for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if nr < h && nc < w {
                        let d = dist[r][c] + u32::from(g[nr][nc] == b'#');
                        if d < dist[nr][nc] {
                            dist[nr][nc] = d;
                            changed = true;
                        }
                    }
                }
            }
        }
    }
    dist[h - 1][w - 1]
}
