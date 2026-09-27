pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
    let mut used = vec![false; cookies.len()];
    let mut happy = 0;
    for &g in greed {
        if let Some(j) = (0..cookies.len()).find(|&j| !used[j] && cookies[j] >= g) {
            used[j] = true;
            happy += 1;
        }
    }
    happy
}
