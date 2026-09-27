pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
    let mut bed = bed.to_vec();
    for _ in 0..n {
        let spot = (0..bed.len()).find(|&i| {
            !bed[i] && (i == 0 || !bed[i - 1]) && (i + 1 == bed.len() || !bed[i + 1])
        });
        match spot {
            Some(i) => bed[i] = true,
            None => return false,
        }
    }
    true
}
