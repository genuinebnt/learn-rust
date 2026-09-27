pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
    // below[c] = the cheapest walk from (r, c) down to the bottom, filled from the last row up.
    let mut below: Vec<i64> = triangle[triangle.len() - 1].iter().map(|&x| x as i64).collect();
    for row in triangle.iter().rev().skip(1) {
        for (c, &x) in row.iter().enumerate() {
            below[c] = x as i64 + below[c].min(below[c + 1]);
        }
    }
    below[0]
}
