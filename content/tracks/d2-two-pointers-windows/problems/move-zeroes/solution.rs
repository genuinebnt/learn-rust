pub fn move_zeroes(nums: &mut [i32]) {
    let mut write = 0;
    for read in 0..nums.len() {
        if nums[read] != 0 {
            nums.swap(write, read);
            write += 1;
        }
    }
}
