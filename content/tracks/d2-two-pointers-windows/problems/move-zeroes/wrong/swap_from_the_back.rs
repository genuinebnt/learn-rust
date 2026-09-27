pub fn move_zeroes(nums: &mut [i32]) {
    let (mut l, mut r) = (0, nums.len());
    while l < r {
        if nums[l] == 0 {
            r -= 1;
            nums.swap(l, r);
        } else {
            l += 1;
        }
    }
}
