//! Strict text to integer conversion.

#[derive(Debug, PartialEq, Eq)]
pub enum IntError {
    Empty,
    Invalid,
    OutOfRange,
}

pub fn parse_sql_int(s: &str) -> Result<i64, IntError> {
    todo!("3a-c3: trim, sign, digits, checked accumulation")
}
