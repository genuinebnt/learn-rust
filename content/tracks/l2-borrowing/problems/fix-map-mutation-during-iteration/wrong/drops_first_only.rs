use std::collections::HashMap;

/// Removes every entry whose count is zero.
pub fn drop_zero(counts: &mut HashMap<String, u32>) {
    let zero = counts.iter().find(|(_, v)| **v == 0).map(|(k, _)| k.to_string());
    if let Some(k) = zero {
        counts.remove(&k);
    }
}
