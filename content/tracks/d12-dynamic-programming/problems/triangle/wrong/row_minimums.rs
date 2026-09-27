pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
    triangle.iter().map(|row| *row.iter().min().unwrap() as i64).sum()
}
