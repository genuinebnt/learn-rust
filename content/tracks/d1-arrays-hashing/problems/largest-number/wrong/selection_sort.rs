pub fn largest_number(nums: &[u32]) -> String {
    let mut parts: Vec<String> = nums.iter().map(u32::to_string).collect();
    for i in 0..parts.len() {
        let mut best = i;
        for j in i + 1..parts.len() {
            if parts[j].clone() + &parts[best] > parts[best].clone() + &parts[j] {
                best = j;
            }
        }
        parts.swap(i, best);
    }
    if parts.first().is_some_and(|p| p == "0") {
        return "0".into();
    }
    parts.concat()
}
