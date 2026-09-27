pub fn count_provinces(connected: &[Vec<u8>]) -> usize {
    let n = connected.len();
    let mut reach: Vec<Vec<bool>> = connected.iter().map(|row| row.iter().map(|&x| x == 1).collect()).collect();
    for k in 0..n {
        for i in 0..n {
            if reach[i][k] {
                for j in 0..n {
                    if reach[k][j] {
                        reach[i][j] = true;
                    }
                }
            }
        }
    }
    (0..n).filter(|&i| (0..i).all(|j| !reach[i][j])).count()
}
