use std::collections::VecDeque;

pub fn minutes_to_rot(grid: &[Vec<u8>]) -> Option<u32> {
    let mut g = grid.to_vec();
    let (h, w) = (g.len(), g.first().map_or(0, Vec::len));
    let mut queue = VecDeque::new();
    let mut fresh = 0;
    for (r, row) in g.iter().enumerate() {
        for (c, &cell) in row.iter().enumerate() {
            match cell {
                2 => queue.push_back((r, c, 0)),
                1 => fresh += 1,
                _ => {}
            }
        }
    }
    let mut minutes = 0;
    while let Some((r, c, t)) = queue.pop_front() {
        minutes = t;
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < h && nc < w && g[nr][nc] == 1 {
                g[nr][nc] = 2;
                fresh -= 1;
                queue.push_back((nr, nc, t + 1));
            }
        }
    }
    (fresh == 0).then_some(minutes)
}
