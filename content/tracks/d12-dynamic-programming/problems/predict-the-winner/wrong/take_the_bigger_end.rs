pub fn predict_the_winner(nums: &[u32]) -> bool {
    let (mut lo, mut hi) = (0, nums.len());
    let mut scores = [0u64; 2];
    let mut turn = 0;
    while lo < hi {
        if nums[lo] >= nums[hi - 1] {
            scores[turn] += nums[lo] as u64;
            lo += 1;
        } else {
            scores[turn] += nums[hi - 1] as u64;
            hi -= 1;
        }
        turn ^= 1;
    }
    scores[0] >= scores[1]
}
