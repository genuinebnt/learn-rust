pub fn concat_twice(nums: &[i32]) -> Vec<i32> {
    let mut out = nums.to_vec();
    out.extend_from_slice(nums.get(1..).unwrap_or(&[]));
    out
}
