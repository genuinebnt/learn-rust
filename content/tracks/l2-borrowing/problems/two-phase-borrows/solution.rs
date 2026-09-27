pub fn push_lengths(v: &mut Vec<usize>, n: usize) {
    for _ in 0..n {
        // Two-phase borrow: `&mut v` is reserved, `v.len()` reads, then the push activates.
        v.push(v.len());
    }
}
