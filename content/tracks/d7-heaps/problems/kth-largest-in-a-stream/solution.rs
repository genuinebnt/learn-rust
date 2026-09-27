use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub struct KthLargest {
    k: usize,
    /// The k largest values so far; the smallest of them is on top.
    heap: BinaryHeap<Reverse<i32>>,
}

impl KthLargest {
    pub fn new(k: usize, nums: &[i32]) -> Self {
        let mut s = KthLargest { k, heap: BinaryHeap::with_capacity(k + 1) };
        for &x in nums {
            s.add(x);
        }
        s
    }

    pub fn add(&mut self, val: i32) -> Option<i32> {
        self.heap.push(Reverse(val));
        if self.heap.len() > self.k {
            self.heap.pop();
        }
        if self.heap.len() < self.k {
            return None;
        }
        self.heap.peek().map(|&Reverse(x)| x)
    }
}
