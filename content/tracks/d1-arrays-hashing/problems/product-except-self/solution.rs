pub fn product_except_self(nums: &[i32]) -> Vec<i32> {
    let n = nums.len();
    let mut out = vec![1; n];
    let mut prefix = 1;
    for i in 0..n {
        out[i] = prefix;
        prefix *= nums[i];
    }
    let mut suffix = 1;
    for i in (0..n).rev() {
        out[i] *= suffix;
        suffix *= nums[i];
    }
    out
}
