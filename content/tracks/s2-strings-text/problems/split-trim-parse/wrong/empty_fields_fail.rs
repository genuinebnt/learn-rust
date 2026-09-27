use std::num::ParseIntError;

pub fn sum_csv(line: &str) -> Result<i64, ParseIntError> {
    line.split(',').map(str::trim).map(str::parse::<i64>).sum()
}
