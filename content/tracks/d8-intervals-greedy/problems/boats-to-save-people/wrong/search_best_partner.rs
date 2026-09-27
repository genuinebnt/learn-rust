pub fn num_rescue_boats(people: &[u32], limit: u32) -> usize {
    let mut w = people.to_vec();
    w.sort_unstable();
    let mut used = vec![false; w.len()];
    let mut boats = 0;
    for i in (0..w.len()).rev() {
        if used[i] {
            continue;
        }
        used[i] = true;
        boats += 1;
        if let Some(j) = (0..i).rev().find(|&j| !used[j] && w[i] as u64 + w[j] as u64 <= limit as u64) {
            used[j] = true;
        }
    }
    boats
}
