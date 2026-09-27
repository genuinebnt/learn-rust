pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
    let mut w = people.to_vec();
    w.sort_unstable();
    let (mut i, mut boats) = (0, 0);
    while i < w.len() {
        if i + 1 < w.len() && w[i] as u64 + w[i + 1] as u64 <= limit as u64 {
            i += 2;
        } else {
            i += 1;
        }
        boats += 1;
    }
    boats
}
