pub fn first_missing_positive(nums: &mut [i32]) -> i32 {
    (1..).find(|x| !nums.contains(x)).unwrap()
}
