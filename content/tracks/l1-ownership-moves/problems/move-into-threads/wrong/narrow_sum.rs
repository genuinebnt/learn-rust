use std::thread;

pub fn parallel_sum(chunks: Vec<Vec<u64>>) -> u64 {
    let handles: Vec<_> = chunks
        .into_iter()
        .map(|chunk| thread::spawn(move || chunk.iter().map(|&x| x as u32).sum::<u32>()))
        .collect();
    handles.into_iter().map(|h| h.join().expect("worker panicked") as u64).sum()
}
