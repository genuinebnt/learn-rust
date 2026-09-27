pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
    let mut w = people.to_vec();
    w.sort_unstable();
    let (mut lo, mut hi) = (0usize, w.len());
    let mut boats = 0;
    while lo < hi {
        // The heaviest left takes a boat, with the lightest if they fit together.
        hi -= 1;
        if lo < hi && w[lo] as u64 + w[hi] as u64 <= limit as u64 {
            lo += 1;
        }
        boats += 1;
    }
    boats
}
