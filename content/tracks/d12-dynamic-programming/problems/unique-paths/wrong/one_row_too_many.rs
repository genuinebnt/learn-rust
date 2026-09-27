pub fn unique_paths(m: usize, n: usize) -> u64 {
    let mut row = vec![1u64; n];
    for _ in 0..m {
        for j in 1..n {
            row[j] += row[j - 1];
        }
    }
    row[n - 1]
}
