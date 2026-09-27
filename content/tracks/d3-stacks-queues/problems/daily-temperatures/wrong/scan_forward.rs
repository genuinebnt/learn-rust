pub fn daily_temperatures(temps: &[i32]) -> Vec<usize> {
    let n = temps.len();
    (0..n).map(|i| (i + 1..n).find(|&j| temps[j] > temps[i]).map_or(0, |j| j - i)).collect()
}
