/// `v` is sorted. Moves the values to the front so each appears at most `k` times (k ≥ 1), in order, and
/// returns how many there are. O(n) time, O(1) extra space.
pub fn dedup_keep(v: &mut [i32], k: usize) -> usize {
    let mut write = 0;
    for read in 0..v.len() {
        if read < k || v[read] != v[read - k] {
            v[write] = v[read];
            write += 1;
        }
    }
    write
}

/// The same on a `Vec`: drop the extra copies in place.
pub fn dedup_keep_vec(v: &mut Vec<i32>, k: usize) {
    let n = dedup_keep(v, k);
    v.truncate(n);
}
