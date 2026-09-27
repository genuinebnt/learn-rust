pub fn maximal_square(matrix: &[&str]) -> usize {
    let cols = matrix.first().map_or(0, |r| r.len());
    let mut side = vec![0usize; cols + 1];
    let mut best = 0;
    for row in matrix {
        for (j, &b) in row.as_bytes().iter().enumerate() {
            side[j + 1] = if b == b'1' { 1 + side[j + 1].min(side[j]) } else { 0 };
            best = best.max(side[j + 1]);
        }
    }
    best * best
}
