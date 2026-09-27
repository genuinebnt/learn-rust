pub fn unique_paths(m: usize, n: usize) -> u64 {
    let fact = |k: usize| (1..=k as u64).product::<u64>();
    fact(m + n - 2) / (fact(m - 1) * fact(n - 1))
}
