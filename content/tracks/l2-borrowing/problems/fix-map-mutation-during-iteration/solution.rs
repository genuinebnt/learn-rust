use std::collections::HashMap;

/// Removes every entry whose count is zero.
pub fn drop_zero(counts: &mut HashMap<String, u32>) {
    counts.retain(|_, v| *v != 0);
}
