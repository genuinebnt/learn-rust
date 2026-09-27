fn entry(r: u64, k: u64) -> u64 {
    if k == 0 || k == r { 1 } else { entry(r - 1, k - 1) + entry(r - 1, k) }
}

pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
    (0..num_rows as u64).map(|r| (0..=r).map(|k| entry(r, k)).collect()).collect()
}
