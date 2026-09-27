use std::collections::BinaryHeap;

pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
    let mut heap = BinaryHeap::from(stones.to_vec());
    while let Some(y) = heap.pop() {
        let Some(x) = heap.pop() else {
            return Some(y);
        };
        if y > x {
            heap.push(y - x);
        }
    }
    None
}
