pub fn chunk_sums(v: &[i32], size: usize) -> Vec<i32> {
    v.chunks(size).map(|c| c.iter().sum()).collect()
}

pub fn max_window_sum(v: &[i32], k: usize) -> Option<i32> {
    if v.len() < k {
        return None;
    }
    Some(v.windows(k).map(|w| w.iter().sum()).fold(0, i32::max))
}
