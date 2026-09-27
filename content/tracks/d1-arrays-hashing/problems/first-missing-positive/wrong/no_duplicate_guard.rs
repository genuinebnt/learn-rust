pub fn first_missing_positive(nums: &mut [i32]) -> i32 {
    let n = nums.len();
    for i in 0..n {
        while nums[i] > 0 && (nums[i] as usize) <= n && nums[i] as usize != i + 1 {
            let home = nums[i] as usize - 1;
            nums.swap(i, home);
        }
    }
    (0..n).find(|&i| nums[i] != i as i32 + 1).map_or(n as i32 + 1, |i| i as i32 + 1)
}
