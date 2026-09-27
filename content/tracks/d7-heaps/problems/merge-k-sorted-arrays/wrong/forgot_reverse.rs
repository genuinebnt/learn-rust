use std::collections::BinaryHeap;

pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
    let mut out = Vec::new();
    let mut heap: BinaryHeap<(i32, usize, usize)> =
        arrays.iter().enumerate().filter_map(|(a, v)| v.first().map(|&x| (x, a, 0))).collect();
    while let Some((x, a, i)) = heap.pop() {
        out.push(x);
        if let Some(&next) = arrays[a].get(i + 1) {
            heap.push((next, a, i + 1));
        }
    }
    out
}
