use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
    let mut heap: BinaryHeap<Reverse<u32>> = stones.iter().map(|&s| Reverse(s)).collect();
    while let Some(Reverse(x)) = heap.pop() {
        let Some(Reverse(y)) = heap.pop() else {
            return Some(x);
        };
        if y > x {
            heap.push(Reverse(y - x));
        }
    }
    None
}
