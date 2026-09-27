pub struct KthLargest {
    k: usize,
    all: Vec<i32>,
}

impl KthLargest {
    pub fn new(k: usize, nums: &[i32]) -> Self {
        KthLargest { k, all: nums.to_vec() }
    }

    pub fn add(&mut self, val: i32) -> Option<i32> {
        self.all.push(val);
        if self.all.len() < self.k {
            return None;
        }
        let k = self.k;
        Some(*self.all.select_nth_unstable_by(k - 1, |a, b| b.cmp(a)).1)
    }
}
