pub fn maximal_square(matrix: &[&str]) -> usize {
    let cols = matrix.first().map_or(0, |r| r.len());
    let mut side = vec![0usize; cols + 1];
    let mut best = 0;
    for row in matrix {
        let mut up_left = 0;
        for (j, &b) in row.as_bytes().iter().enumerate() {
            let up = side[j + 1];
            side[j + 1] = if b == b'1' { 1 + up_left.min(up).min(side[j]) } else { 0 };
            up_left = up;
            best = best.max(side[j + 1]);
        }
    }
    best
}
