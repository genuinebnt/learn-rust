pub fn largest_number(nums: &[u32]) -> String {
    let mut parts: Vec<String> = nums.iter().map(u32::to_string).collect();
    parts.sort_unstable_by(|a, b| (b.clone() + a).cmp(&(a.clone() + b)));
    parts.concat()
}
