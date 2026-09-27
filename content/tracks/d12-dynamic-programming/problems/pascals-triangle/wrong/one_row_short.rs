pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
    let mut rows: Vec<Vec<u64>> = vec![vec![1]];
    for r in 1..num_rows.saturating_sub(1).max(1) {
        let above = &rows[r - 1];
        let mut row = vec![1];
        row.extend(above.windows(2).map(|w| w[0] + w[1]));
        row.push(1);
        rows.push(row);
    }
    rows
}
