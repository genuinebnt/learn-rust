fn hits(nums: &[u32], left: u32) -> bool {
    left == 0 || matches!(nums, [x, rest @ ..] if (*x <= left && hits(rest, left - x)) || hits(rest, left))
}

pub fn can_partition(nums: &[u32]) -> bool {
    let total: u32 = nums.iter().sum();
    total % 2 == 0 && hits(nums, total / 2)
}
