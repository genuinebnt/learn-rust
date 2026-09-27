use std::collections::HashMap;

/// Removes every entry whose count is zero.
pub fn drop_zero(counts: &mut HashMap<String, u32>) {
    for (k, v) in counts.iter() {
        if *v == 0 {
            counts.remove(k);
        }
    }
}
