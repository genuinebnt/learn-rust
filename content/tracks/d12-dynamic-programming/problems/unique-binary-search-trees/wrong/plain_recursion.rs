pub fn num_trees(n: u32) -> u64 {
    if n == 0 { 1 } else { (0..n).map(|l| num_trees(l) * num_trees(n - 1 - l)).sum() }
}
