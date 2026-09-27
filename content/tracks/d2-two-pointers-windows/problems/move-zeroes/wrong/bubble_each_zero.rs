pub fn move_zeroes(nums: &mut [i32]) {
    let n = nums.len();
    let mut end = n;
    let mut i = 0;
    while i < end {
        if nums[i] == 0 {
            for j in i..n - 1 {
                nums.swap(j, j + 1);
            }
            end -= 1;
        } else {
            i += 1;
        }
    }
}
