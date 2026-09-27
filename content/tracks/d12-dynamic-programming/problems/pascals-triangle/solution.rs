pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
    let mut rows: Vec<Vec<u64>> = Vec::with_capacity(num_rows);
    for r in 0..num_rows {
        let mut row = Vec::with_capacity(r + 1);
        row.push(1);
        if let Some(above) = rows.last() {
            row.extend(above.windows(2).map(|w| w[0] + w[1]));
            row.push(1);
        }
        rows.push(row);
    }
    rows
}
