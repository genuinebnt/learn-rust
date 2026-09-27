use std::collections::BinaryHeap;

pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
    let mut heap = BinaryHeap::from(stones.to_vec());
    while heap.len() > 1 {
        let y = heap.pop().unwrap();
        let x = heap.pop().unwrap();
        heap.push(y - x);
    }
    heap.pop()
}
