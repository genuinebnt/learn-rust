pub fn unique_paths(m: usize, n: usize) -> u64 {
    // row[j] = paths to (i, j). The first row is all 1s (only moves right).
    let mut row = vec![1u64; n];
    for _ in 1..m {
        for j in 1..n {
            row[j] += row[j - 1]; // above (old row[j]) + left (new row[j - 1])
        }
    }
    row[n - 1]
}
