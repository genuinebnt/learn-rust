#[derive(Debug, PartialEq)]
pub enum CsvError {
    /// Field `n` (counting from 1) is empty.
    Empty(usize),
    /// Field `n` isn't an integer; the trimmed text.
    Bad(usize, String),
    /// A running total doesn't fit in an `i64`.
    Overflow,
}

pub fn sum_csv(line: &str) -> Result<i64, CsvError> {
    todo!()
}

#[derive(Debug, PartialEq)]
pub struct LogLine<'a> {
    pub date: &'a str,
    pub time: &'a str,
    pub level: &'a str,
    pub message: &'a str,
    pub millis: Option<u64>,
}

pub fn parse_log(line: &str) -> Option<LogLine<'_>> {
    todo!()
}
