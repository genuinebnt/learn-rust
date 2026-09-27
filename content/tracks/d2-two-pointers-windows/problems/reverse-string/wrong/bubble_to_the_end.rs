pub fn reverse_in_place(s: &mut [u8]) {
    // Carry the first byte to the end, then the new first byte to one before it, and so on.
    let n = s.len();
    for done in 0..n {
        for j in 0..n - 1 - done {
            s.swap(j, j + 1);
        }
    }
}
