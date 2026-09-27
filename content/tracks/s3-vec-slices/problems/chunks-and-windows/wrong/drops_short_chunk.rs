pub fn chunk_sums(v: &[i32], size: usize) -> Vec<i32> {
    v.chunks_exact(size).map(|c| c.iter().sum()).collect()
}

pub fn max_window_sum(v: &[i32], k: usize) -> Option<i32> {
    v.windows(k).map(|w| w.iter().sum()).max()
}
