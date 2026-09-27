pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
    let fact = |n: u64| (1..=n).product::<u64>();
    (0..num_rows as u64).map(|r| (0..=r).map(|k| fact(r) / (fact(k) * fact(r - k))).collect()).collect()
}
