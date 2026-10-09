//! How much of the log may be deleted after a checkpoint.

/// The smallest LSN recovery can still need.
pub fn truncation_lsn(checkpoint_begin: u64, dirty_rec_lsns: &[u64], active_first_lsns: &[u64]) -> u64 {
    todo!("4c-c1: the smallest of the checkpoint start, the oldest dirty-page record and the oldest active transaction's first record")
}
