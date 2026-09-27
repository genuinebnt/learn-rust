pub fn subarray_sum(nums: &[i32], k: i32) -> usize {
    let mut count = 0;
    for i in 0..nums.len() {
        let mut sum = 0;
        for &x in &nums[i..] {
            sum += x;
            if sum == k {
                count += 1;
            }
        }
    }
    count
}
