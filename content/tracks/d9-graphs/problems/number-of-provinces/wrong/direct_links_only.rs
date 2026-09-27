pub fn count_provinces(connected: &[Vec<u8>]) -> usize {
    // A city starts a new province unless it links directly to an earlier city.
    let n = connected.len();
    (0..n).filter(|&i| (0..i).all(|j| connected[i][j] == 0)).count()
}
