pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
    if lists.is_empty() || lists.iter().any(|l| l.is_empty()) {
        return None;
    }
    let mut pos = vec![0; lists.len()];
    let mut best: Option<(i32, i32)> = None;
    loop {
        let lo_list = (0..lists.len()).min_by_key(|&l| lists[l][pos[l]]).unwrap();
        let lo = lists[lo_list][pos[lo_list]];
        let hi = (0..lists.len()).map(|l| lists[l][pos[l]]).max().unwrap();
        if best.is_none_or(|(a, b)| (hi as i64 - lo as i64) < (b as i64 - a as i64)) {
            best = Some((lo, hi));
        }
        pos[lo_list] += 1;
        if pos[lo_list] == lists[lo_list].len() {
            return best;
        }
    }
}
