//! Garbage collection of one row's version chain.

/// `chain` is `(commit_ts, value)` newest first. Removes what no reader at or above `watermark` can see; returns how many versions went.
pub fn gc_chain(chain: &mut Vec<(u64, i64)>, watermark: u64) -> usize {
    let before = chain.len();
    chain.retain(|&(ts, _)| ts > watermark);
    before - chain.len()
}

/// The value a reader with timestamp `read_ts` sees.
pub fn read_at(chain: &[(u64, i64)], read_ts: u64) -> Option<i64> {
    chain.iter().find(|&&(ts, _)| ts <= read_ts).map(|&(_, v)| v)
}
