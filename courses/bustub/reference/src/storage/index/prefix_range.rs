//! The upper bound of a prefix scan.

/// The smallest byte string greater than every string that starts with `prefix`; `None` if there is no such string.
pub fn prefix_end(prefix: &[u8]) -> Option<Vec<u8>> {
    // @begin 2c-c3
    let mut end = prefix.to_vec();
    while let Some(&last) = end.last() {
        if last == 0xFF {
            end.pop();
        } else {
            *end.last_mut().unwrap() += 1;
            return Some(end);
        }
    }
    None
    //~ todo!("2c-c3: drop trailing 0xFF bytes, add one to the last byte left")
    // @end
}
