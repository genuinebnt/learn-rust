use std::num::ParseIntError;

pub fn parse_optional(s: Option<&str>) -> Result<Option<i32>, ParseIntError> {
    s.map(|t| t.parse::<i64>().map(|n| n as i32)).transpose()
}
