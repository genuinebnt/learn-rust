pub fn subarray_sum(nums: &[i32], k: i32) -> usize {
    let (mut left, mut sum, mut count) = (0, 0, 0);
    for right in 0..nums.len() {
        sum += nums[right];
        while sum > k && left < right {
            sum -= nums[left];
            left += 1;
        }
        if sum == k {
            count += 1;
        }
    }
    count
}
