use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {
    let (h, w) = (heights.len(), heights[0].len());
    let mut best = vec![vec![u32::MAX; w]; h];
    best[0][0] = 0;
    let mut heap = BinaryHeap::from([Reverse((0u32, 0usize, 0usize))]);
    while let Some(Reverse((effort, r, c))) = heap.pop() {
        if effort > best[r][c] {
            continue;
        }
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < h && nc < w {
                let next = effort + heights[r][c].abs_diff(heights[nr][nc]);
                if next < best[nr][nc] {
                    best[nr][nc] = next;
                    heap.push(Reverse((next, nr, nc)));
                }
            }
        }
    }
    best[h - 1][w - 1]
}
