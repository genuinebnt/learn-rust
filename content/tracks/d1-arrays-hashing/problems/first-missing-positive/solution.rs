pub fn first_missing_positive(nums: &mut [i32]) -> i32 {
    let n = nums.len();
    for i in 0..n {
        // Keep swapping nums[i] into its home slot until it's out of range or already home.
        while nums[i] > 0 && (nums[i] as usize) <= n && nums[nums[i] as usize - 1] != nums[i] {
            let home = nums[i] as usize - 1;
            nums.swap(i, home);
        }
    }
    (0..n).find(|&i| nums[i] != i as i32 + 1).map_or(n as i32 + 1, |i| i as i32 + 1)
}
