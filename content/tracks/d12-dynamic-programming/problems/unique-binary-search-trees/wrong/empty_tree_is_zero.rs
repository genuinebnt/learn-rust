pub fn num_trees(n: u32) -> u64 {
    let n = n as usize;
    let mut trees = vec![0u64; n + 1];
    trees[0] = 1;
    for k in 1..=n {
        trees[k] = (0..k).map(|left| trees[left] * trees[k - 1 - left]).sum();
    }
    if n == 0 { 0 } else { trees[n] }
}
