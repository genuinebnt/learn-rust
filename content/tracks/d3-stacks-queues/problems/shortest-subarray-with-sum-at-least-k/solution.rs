use std::collections::VecDeque;

pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
    let mut prefix = vec![0i64; nums.len() + 1];
    for (i, &x) in nums.iter().enumerate() {
        prefix[i + 1] = prefix[i] + x;
    }
    let mut best: Option<usize> = None;
    // Start indices with increasing prefix sums: the only useful left ends.
    let mut starts: VecDeque<usize> = VecDeque::new();
    for (j, &pj) in prefix.iter().enumerate() {
        while let Some(&i) = starts.front() {
            if pj - prefix[i] < k {
                break;
            }
            best = Some(best.map_or(j - i, |b| b.min(j - i)));
            starts.pop_front();
        }
        while starts.back().is_some_and(|&i| prefix[i] >= pj) {
            starts.pop_back();
        }
        starts.push_back(j);
    }
    best
}
