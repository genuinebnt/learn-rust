pub fn num_trees(n: u32) -> u64 {
    let n = n as usize;
    // trees[k] = shapes of a BST with k keys. With root r, the left side has r - 1
    // keys and the right side k - r, and any left shape pairs with any right shape.
    let mut trees = vec![0u64; n + 1];
    trees[0] = 1;
    for k in 1..=n {
        trees[k] = (0..k).map(|left| trees[left] * trees[k - 1 - left]).sum();
    }
    trees[n]
}
