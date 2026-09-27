use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap};

#[derive(Default)]
pub struct MedianFinder {
    /// The smaller half, largest on top.
    low: BinaryHeap<i32>,
    /// The larger half, smallest on top.
    high: BinaryHeap<Reverse<i32>>,
    /// Live sizes of the halves (the heaps may also hold removed copies).
    low_len: usize,
    high_len: usize,
    /// Copies of each value still in the stream.
    live: HashMap<i32, usize>,
    /// Removed copies still sitting inside a heap, dropped when they reach a top.
    doomed: HashMap<i32, usize>,
}

impl MedianFinder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add_num(&mut self, num: i32) {
        *self.live.entry(num).or_insert(0) += 1;
        if self.low.peek().is_none_or(|&top| num <= top) {
            self.low.push(num);
            self.low_len += 1;
        } else {
            self.high.push(Reverse(num));
            self.high_len += 1;
        }
        self.rebalance();
    }

    pub fn remove_num(&mut self, num: i32) -> bool {
        match self.live.get_mut(&num) {
            Some(c) => {
                *c -= 1;
                if *c == 0 {
                    self.live.remove(&num);
                }
            }
            None => return false,
        }
        *self.doomed.entry(num).or_insert(0) += 1;
        // Tops are always live, so this says which half the copy belongs to.
        if self.low.peek().is_some_and(|&top| num < top) {
            self.low_len -= 1;
        } else {
            self.high_len -= 1;
        }
        self.prune();
        self.rebalance();
        true
    }

    /// `&self` works because every mutation leaves both tops live.
    pub fn find_median(&self) -> Option<f64> {
        let &lo = self.low.peek()?;
        if self.low_len > self.high_len {
            return Some(lo as f64);
        }
        let &Reverse(hi) = self.high.peek()?;
        // In f64, not i32: i32::MAX + i32::MAX overflows.
        Some((lo as f64 + hi as f64) / 2.0)
    }

    fn take_doomed(&mut self, v: i32) -> bool {
        match self.doomed.get_mut(&v) {
            Some(c) => {
                *c -= 1;
                if *c == 0 {
                    self.doomed.remove(&v);
                }
                true
            }
            None => false,
        }
    }

    /// Pops removed copies off both tops.
    fn prune(&mut self) {
        while let Some(&top) = self.low.peek() {
            if !self.take_doomed(top) {
                break;
            }
            self.low.pop();
        }
        while let Some(&Reverse(top)) = self.high.peek() {
            if !self.take_doomed(top) {
                break;
            }
            self.high.pop();
        }
    }

    /// Keeps low_len == high_len or low_len == high_len + 1.
    fn rebalance(&mut self) {
        if self.low_len > self.high_len + 1 {
            if let Some(x) = self.low.pop() {
                self.high.push(Reverse(x));
                self.low_len -= 1;
                self.high_len += 1;
            }
            self.prune();
        } else if self.high_len > self.low_len {
            if let Some(Reverse(x)) = self.high.pop() {
                self.low.push(x);
                self.high_len -= 1;
                self.low_len += 1;
            }
            self.prune();
        }
    }
}
