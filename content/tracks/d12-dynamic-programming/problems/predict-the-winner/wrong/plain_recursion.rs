fn lead(nums: &[u32]) -> i64 {
    match nums {
        [] => 0,
        [x] => *x as i64,
        [first, .., last] => (*first as i64 - lead(&nums[1..])).max(*last as i64 - lead(&nums[..nums.len() - 1])),
    }
}

pub fn predict_the_winner(nums: &[u32]) -> bool {
    lead(nums) >= 0
}
