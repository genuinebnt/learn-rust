//! The upper bound of a prefix scan.

/// The smallest byte string greater than every string that starts with `prefix`; `None` if there is no such string.
pub fn prefix_end(prefix: &[u8]) -> Option<Vec<u8>> {
    todo!("2c-c3: drop trailing 0xFF bytes, add one to the last byte left")
}
