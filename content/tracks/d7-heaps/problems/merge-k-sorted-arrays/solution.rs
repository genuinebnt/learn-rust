use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
    let total = arrays.iter().map(Vec::len).sum();
    let mut out = Vec::with_capacity(total);
    // One candidate per array: (value, which array, index in it).
    let mut heap: BinaryHeap<Reverse<(i32, usize, usize)>> =
        arrays.iter().enumerate().filter_map(|(a, v)| v.first().map(|&x| Reverse((x, a, 0)))).collect();
    while let Some(Reverse((x, a, i))) = heap.pop() {
        out.push(x);
        if let Some(&next) = arrays[a].get(i + 1) {
            heap.push(Reverse((next, a, i + 1)));
        }
    }
    out
}
