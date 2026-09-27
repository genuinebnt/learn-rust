pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
    let mut bed = bed.to_vec();
    let mut planted = 0;
    for i in 0..bed.len() {
        let left = i == 0 || !bed[i - 1];
        let right = i + 1 == bed.len() || !bed[i + 1];
        if !bed[i] && left && right {
            bed[i] = true;
            planted += 1;
        }
    }
    planted > n || n == 0
}
