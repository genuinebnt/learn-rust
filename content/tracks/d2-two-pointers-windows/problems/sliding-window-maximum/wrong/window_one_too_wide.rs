use std::collections::VecDeque;

pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
    let mut dq: VecDeque<usize> = VecDeque::new();
    let mut out = Vec::with_capacity(nums.len() + 1 - k);
    for i in 0..nums.len() {
        if dq.front().is_some_and(|&f| f + k < i) {
            dq.pop_front();
        }
        while dq.back().is_some_and(|&b| nums[b] <= nums[i]) {
            dq.pop_back();
        }
        dq.push_back(i);
        if i + 1 >= k {
            out.push(nums[dq[0]]);
        }
    }
    out
}
