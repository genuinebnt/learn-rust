use std::collections::VecDeque;

pub fn minutes_to_rot(grid: &[Vec<u8>]) -> Option<u32> {
    let mut g = grid.to_vec();
    let (h, w) = (g.len(), g[0].len());
    let mut queue = VecDeque::new();
    let mut fresh = 0;
    for r in 0..h {
        for c in 0..w {
            match g[r][c] {
                2 => queue.push_back((r, c)),
                1 => fresh += 1,
                _ => {}
            }
        }
    }
    let mut minutes = 0;
    while !queue.is_empty() {
        for _ in 0..queue.len() {
            let (r, c) = queue.pop_front().unwrap();
            for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                if nr < h && nc < w && g[nr][nc] == 1 {
                    g[nr][nc] = 2;
                    fresh -= 1;
                    queue.push_back((nr, nc));
                }
            }
        }
        minutes += 1;
    }
    (fresh == 0).then_some(minutes)
}
