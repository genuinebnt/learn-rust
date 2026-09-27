pub fn product_except_self(nums: &[i32]) -> Vec<i32> {
    let nonzero: i32 = nums.iter().filter(|&&x| x != 0).product();
    let has_zero = nums.contains(&0);
    nums.iter()
        .map(|&x| match (x, has_zero) {
            (0, _) => nonzero,
            (_, true) => 0,
            _ => nonzero / x,
        })
        .collect()
}
