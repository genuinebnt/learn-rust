pub fn product_except_self(nums: &[i32]) -> Vec<i32> {
    (0..nums.len())
        .map(|i| nums.iter().enumerate().filter(|&(j, _)| j != i).map(|(_, &x)| x).product())
        .collect()
}
