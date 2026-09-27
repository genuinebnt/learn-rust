use std::collections::BinaryHeap;

pub struct KthLargest {
    k: usize,
    heap: BinaryHeap<i32>,
}

impl KthLargest {
    pub fn new(k: usize, nums: &[i32]) -> Self {
        KthLargest { k, heap: nums.iter().copied().collect() }
    }

    pub fn add(&mut self, val: i32) -> Option<i32> {
        self.heap.push(val);
        // Pops the largest values: keeps the smallest ones instead.
        while self.heap.len() > self.k {
            self.heap.pop();
        }
        if self.heap.len() < self.k {
            return None;
        }
        self.heap.peek().copied()
    }
}
