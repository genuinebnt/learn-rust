fn need(d: &[Vec<i32>], i: usize, j: usize) -> i64 {
    let (m, n) = (d.len(), d[0].len());
    let next = if i + 1 == m && j + 1 == n {
        1
    } else {
        let down = if i + 1 < m { need(d, i + 1, j) } else { i64::MAX };
        let right = if j + 1 < n { need(d, i, j + 1) } else { i64::MAX };
        down.min(right)
    };
    (next - d[i][j] as i64).max(1)
}

pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
    need(dungeon, 0, 0)
}
