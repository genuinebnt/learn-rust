pub fn unique_paths(m: usize, n: usize) -> u64 {
    if m == 1 || n == 1 { 1 } else { unique_paths(m - 1, n) + unique_paths(m, n - 1) }
}
