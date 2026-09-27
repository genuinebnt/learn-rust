pub fn subsets(nums: &[i32]) -> Vec<Vec<i32>> {
    let mut out = vec![Vec::new()];
    for i in 0..nums.len() {
        for j in i + 1..=nums.len() {
            out.push(nums[i..j].to_vec());
        }
    }
    out
}
