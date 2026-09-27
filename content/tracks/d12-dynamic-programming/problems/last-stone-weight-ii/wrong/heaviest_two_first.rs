use std::collections::BinaryHeap;

pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
    let mut heap: BinaryHeap<u32> = stones.iter().copied().collect();
    while heap.len() > 1 {
        let y = heap.pop().unwrap();
        let x = heap.pop().unwrap();
        if y > x {
            heap.push(y - x);
        }
    }
    heap.pop().unwrap_or(0)
}
