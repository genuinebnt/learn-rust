use std::collections::BinaryHeap;

/// Squared distance. |i32::MIN|² · 2 = 2⁶³, one past i64::MAX, so this is u64.
fn dist2(x: i32, y: i32) -> u64 {
    let (x, y) = (x.unsigned_abs() as u64, y.unsigned_abs() as u64);
    x * x + y * y
}

pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
    if k == 0 {
        return Vec::new();
    }
    // The k best so far; the worst of them (farthest, then largest (x, y)) is on top.
    let mut heap: BinaryHeap<(u64, i32, i32)> = BinaryHeap::with_capacity(k + 1);
    for &(x, y) in points {
        let key = (dist2(x, y), x, y);
        if heap.len() < k {
            heap.push(key);
        } else if heap.peek().is_some_and(|&top| key < top) {
            heap.pop();
            heap.push(key);
        }
    }
    heap.into_sorted_vec().into_iter().map(|(_, x, y)| (x, y)).collect()
}
