pub fn top_k_frequent(nums: &[i32], k: usize) -> Vec<i32> {
    let mut distinct: Vec<i32> = Vec::new();
    for &x in nums {
        if !distinct.contains(&x) {
            distinct.push(x);
        }
    }
    let mut by_count: Vec<(i32, usize)> = distinct.iter().map(|&x| (x, nums.iter().filter(|&&y| y == x).count())).collect();
    by_count.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
    by_count.into_iter().take(k).map(|(x, _)| x).collect()
}
