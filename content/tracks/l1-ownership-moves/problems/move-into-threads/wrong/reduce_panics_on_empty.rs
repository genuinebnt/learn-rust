use std::thread;

pub fn parallel_sum(chunks: Vec<Vec<u64>>) -> u64 {
    let handles: Vec<_> = chunks
        .into_iter()
        .map(|chunk| thread::spawn(move || chunk.into_iter().reduce(|a, b| a + b).unwrap()))
        .collect();
    handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
}
