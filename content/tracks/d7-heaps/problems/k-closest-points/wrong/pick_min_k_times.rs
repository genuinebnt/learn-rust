pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
    let key = |&(x, y): &(i32, i32)| {
        let (a, b) = (x.unsigned_abs() as u64, y.unsigned_abs() as u64);
        (a * a + b * b, x, y)
    };
    let mut left = points.to_vec();
    let mut out = Vec::new();
    while out.len() < k && !left.is_empty() {
        let best = (0..left.len()).min_by_key(|&i| key(&left[i])).unwrap();
        out.push(left.swap_remove(best));
    }
    out
}
