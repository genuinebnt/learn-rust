use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub struct KthLargest {
    k: usize,
    heap: BinaryHeap<Reverse<i32>>,
}

impl KthLargest {
    pub fn new(k: usize, nums: &[i32]) -> Self {
        let mut s = KthLargest { k, heap: BinaryHeap::new() };
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
        self.heap.peek().map(|&Reverse(x)| x)
    }
}
