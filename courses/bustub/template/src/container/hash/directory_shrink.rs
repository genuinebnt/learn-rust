//! When an extendible hash directory may be halved.

/// True when the directory can be halved: the global depth is above 0 and no bucket uses all of it.
pub fn can_shrink(local_depths: &[u32], global_depth: u32) -> bool {
    global_depth > 0 && local_depths.iter().any(|&d| d < global_depth)
}

/// The directory after halving: `slots` must be two identical halves; returns the first half, or `None` otherwise.
pub fn shrink_slots(slots: &[usize]) -> Option<Vec<usize>> {
    if slots.len() % 2 != 0 || slots.is_empty() {
        return None;
    }
    let (lo, hi) = slots.split_at(slots.len() / 2);
    if lo == hi {
        Some(lo.to_vec())
    } else {
        None
    }
}
