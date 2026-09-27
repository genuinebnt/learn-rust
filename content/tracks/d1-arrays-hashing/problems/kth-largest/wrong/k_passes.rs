pub fn kth_largest(nums: &mut [i32], k: usize) -> i32 {
    let mut end = nums.len();
    for _ in 0..k - 1 {
        let (i, _) = nums[..end].iter().enumerate().max_by_key(|&(_, x)| *x).unwrap();
        nums.swap(i, end - 1);
        end -= 1;
    }
    *nums[..end].iter().max().unwrap()
}
