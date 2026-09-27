use std::collections::VecDeque;

pub fn shortest_path_all_keys(grid: &[&str]) -> Option<u32> {
    let g: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
    let (h, w) = (g.len(), g[0].len());
    let mut start = (0, 0);
    let mut all = 0u32;
    for r in 0..h {
        for c in 0..w {
            match g[r][c] {
                b'@' => start = (r, c),
                k @ b'a'..=b'f' => all |= 1 << (k - b'a'),
                _ => {}
            }
        }
    }
    let mut seen = vec![vec![false; w]; h];
    seen[start.0][start.1] = true;
    let mut queue = VecDeque::from([(start.0, start.1, 0u32, 0u32)]);
    while let Some((r, c, keys, steps)) = queue.pop_front() {
        if keys == all {
            return Some(steps);
        }
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr >= h || nc >= w || seen[nr][nc] {
                continue;
            }
            let cell = g[nr][nc];
            let mut held = keys;
            match cell {
                b'#' => continue,
                b'A'..=b'F' if keys & (1 << (cell - b'A')) == 0 => continue,
                b'a'..=b'f' => held |= 1 << (cell - b'a'),
                _ => {}
            }
            seen[nr][nc] = true;
            queue.push_back((nr, nc, held, steps + 1));
        }
    }
    None
}
