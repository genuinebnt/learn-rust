use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
    let mut heap: BinaryHeap<Reverse<(u64, usize)>> = points
        .iter()
        .enumerate()
        .map(|(i, &(x, y))| {
            let (a, b) = (x.unsigned_abs() as u64, y.unsigned_abs() as u64);
            Reverse((a * a + b * b, i))
        })
        .collect();
    let mut out = Vec::new();
    while out.len() < k {
        let Some(Reverse((_, i))) = heap.pop() else { break };
        out.push(points[i]);
    }
    out
}
