pub fn concat_twice(nums: &[i32]) -> Vec<i32> {
    nums.iter().flat_map(|&x| [x, x]).collect()
}
