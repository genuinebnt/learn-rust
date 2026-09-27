pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
    let (m, n) = (dungeon.len(), dungeon[0].len());
    // (running sum, lowest running sum) along the path with the larger sum.
    let mut best = vec![vec![(0i64, 0i64); n]; m];
    for i in 0..m {
        for j in 0..n {
            let prev = match (i, j) {
                (0, 0) => (0, 0),
                (0, _) => best[0][j - 1],
                (_, 0) => best[i - 1][0],
                _ => if best[i - 1][j].0 >= best[i][j - 1].0 { best[i - 1][j] } else { best[i][j - 1] },
            };
            let sum = prev.0 + dungeon[i][j] as i64;
            best[i][j] = (sum, prev.1.min(sum));
        }
    }
    1 - best[m - 1][n - 1].1
}
