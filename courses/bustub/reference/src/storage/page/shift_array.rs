//! Shifting the entries of a fixed array to make room for, or close the gap of, one entry.

/// Inserts `value` at `at` among the first `len` entries. Requires `len < arr.len()` and `at <= len`. Returns the new length.
pub fn insert_at(arr: &mut [u32], len: usize, at: usize, value: u32) -> usize {
    assert!(len < arr.len() && at <= len);
    // @begin 2a-c5
    arr.copy_within(at..len, at + 1);
    //~ for i in at..len {
    //~     arr[i + 1] = arr[i];
    //~ }
    // @end
    arr[at] = value;
    len + 1
}

/// Removes the entry at `at` from the first `len` entries. Requires `at < len`. Returns the new length.
pub fn remove_at(arr: &mut [u32], len: usize, at: usize) -> usize {
    assert!(at < len && len <= arr.len());
    arr.copy_within(at + 1..len, at);
    len - 1
}
