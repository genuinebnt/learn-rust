/// The sum of `nums`, computed by summing each half.
pub fn split_sum(nums: &[i64]) -> i64 {
    if nums.is_empty() {
        return 0;
    }
    let (left, right) = nums.split_at(nums.len() / 2);
    split_sum(left) + split_sum(right)
}
