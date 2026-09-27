pub fn can_partition(nums: &[u32]) -> bool {
    nums.iter().sum::<u32>() % 2 == 0
}
