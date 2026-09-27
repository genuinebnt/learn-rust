pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
    let mut planted = 0;
    let mut left_full = false;
    for i in 0..bed.len() {
        if bed[i] {
            left_full = true;
            continue;
        }
        let right_full = bed.get(i + 1).copied().unwrap_or(false);
        if !left_full && !right_full {
            planted += 1;
            left_full = true;
        } else {
            left_full = false;
        }
    }
    planted >= n
}
