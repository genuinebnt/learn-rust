use std::collections::BinaryHeap;

pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
    if k == 0 {
        return Vec::new();
    }
    let mut heap: BinaryHeap<(i64, i32, i32)> = BinaryHeap::new();
    for &(x, y) in points {
        let (a, b) = (x as i64, y as i64);
        heap.push((a * a + b * b, x, y));
        if heap.len() > k {
            heap.pop();
        }
    }
    heap.into_sorted_vec().into_iter().map(|(_, x, y)| (x, y)).collect()
}
