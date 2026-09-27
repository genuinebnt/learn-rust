pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
    let mut c = 0;
    let mut total = triangle[0][0] as i64;
    for row in &triangle[1..] {
        if row[c + 1] < row[c] {
            c += 1;
        }
        total += row[c] as i64;
    }
    total
}
