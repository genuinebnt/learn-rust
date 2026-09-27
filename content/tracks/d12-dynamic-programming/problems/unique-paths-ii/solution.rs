pub fn unique_paths_with_obstacles(grid: &[Vec<u8>]) -> u64 {
    let n = grid.first().map_or(0, |r| r.len());
    // row[j] = paths to (i, j). Seed one path "arriving" at the start.
    let mut row = vec![0u64; n];
    if n > 0 {
        row[0] = 1;
    }
    for cells in grid {
        for j in 0..n {
            if cells[j] == 1 {
                row[j] = 0;
            } else if j > 0 {
                row[j] += row[j - 1];
            }
        }
    }
    row.last().copied().unwrap_or(0)
}
