pub fn predict_the_winner(nums: &[u32]) -> bool {
    let n = nums.len();
    // For the current i, lead[j] = the mover's best (own score - other's score) on nums[i..=j].
    // Before updating it still holds nums[i + 1..=j].
    let mut lead = vec![0i64; n];
    for i in (0..n).rev() {
        lead[i] = nums[i] as i64;
        for j in i + 1..n {
            lead[j] = (nums[i] as i64 - lead[j]).max(nums[j] as i64 - lead[j - 1]);
        }
    }
    lead.last().map_or(true, |&d| d >= 0)
}
