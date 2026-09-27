pub fn majority(nums: &[i32]) -> i32 {
    *nums.iter().find(|&&x| nums.iter().filter(|&&y| y == x).count() * 2 > nums.len()).unwrap()
}
