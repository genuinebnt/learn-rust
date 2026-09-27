use std::num::ParseIntError;

pub fn sum_csv(line: &str) -> Result<i64, ParseIntError> {
    Ok(line.split(',').filter_map(|f| f.trim().parse::<i64>().ok()).sum())
}
