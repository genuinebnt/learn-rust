pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
    let mut w = people.to_vec();
    w.sort_unstable();
    let (mut lo, mut hi) = (0usize, w.len());
    let mut boats = 0;
    while lo < hi {
        hi -= 1;
        if lo < hi && w[lo] + w[hi] <= limit {
            lo += 1;
        }
        boats += 1;
    }
    boats
}
