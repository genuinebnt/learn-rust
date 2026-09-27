pub fn num_trees(n: u32) -> u64 {
    let fact = |k: u64| (1..=k).product::<u64>();
    let n = n as u64;
    fact(2 * n) / (fact(n + 1) * fact(n))
}
