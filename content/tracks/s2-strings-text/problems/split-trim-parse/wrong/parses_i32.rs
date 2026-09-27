use std::num::ParseIntError;

pub fn sum_csv(line: &str) -> Result<i64, ParseIntError> {
    let mut total = 0i64;
    for f in line.split(',').map(str::trim).filter(|f| !f.is_empty()) {
        total += f.parse::<i32>()? as i64;
    }
    Ok(total)
}
