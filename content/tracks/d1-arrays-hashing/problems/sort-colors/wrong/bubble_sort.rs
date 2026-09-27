pub fn sort_colors(nums: &mut [u8]) {
    for i in 0..nums.len() {
        for j in 0..nums.len() - 1 - i {
            if nums[j] > nums[j + 1] {
                nums.swap(j, j + 1);
            }
        }
    }
}
