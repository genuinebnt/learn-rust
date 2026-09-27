use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn swim_in_water(grid: &[Vec<u32>]) -> u32 {
    let n = grid.len();
    let mut best = vec![vec![u32::MAX; n]; n];
    best[0][0] = 0;
    let mut heap = BinaryHeap::from([Reverse((0u32, 0usize, 0usize))]);
    while let Some(Reverse((t, r, c))) = heap.pop() {
        if (r, c) == (n - 1, n - 1) {
            return t;
        }
        if t > best[r][c] {
            continue;
        }
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < n && nc < n {
                let next = t.max(grid[nr][nc]);
                if next < best[nr][nc] {
                    best[nr][nc] = next;
                    heap.push(Reverse((next, nr, nc)));
                }
            }
        }
    }
    unreachable!()
}
