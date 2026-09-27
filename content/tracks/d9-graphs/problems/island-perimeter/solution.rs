pub fn island_perimeter(grid: &[Vec<u8>]) -> usize {
    let mut sides = 0;
    for (r, row) in grid.iter().enumerate() {
        for (c, &cell) in row.iter().enumerate() {
            if cell == 1 {
                sides += 4;
                // A land neighbour above or to the left hides one side of each cell.
                if r > 0 && grid[r - 1][c] == 1 {
                    sides -= 2;
                }
                if c > 0 && row[c - 1] == 1 {
                    sides -= 2;
                }
            }
        }
    }
    sides
}
