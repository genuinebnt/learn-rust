use std::thread;

/// Sums `data` using up to `chunks` threads.
pub fn parallel_sum(data: &[u64], chunks: usize) -> u64 {
    let size = data.len().div_ceil(chunks.max(1)).max(1);
    thread::scope(|s| {
        let handles: Vec<_> = data
            .chunks_exact(size)
            .map(|chunk| s.spawn(move || chunk.iter().sum::<u64>()))
            .collect();
        handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
    })
}
