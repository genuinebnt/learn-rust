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
    let mut total = 0i64;
    for (i, field) in line.split(',').enumerate() {
        let field = field.trim();
        if field.is_empty() {
            return Err(CsvError::Empty(i + 1));
        }
        let n: i64 = field.parse().map_err(|_| CsvError::Bad(i + 1, field.to_string()))?;
        total = total.checked_add(n).ok_or(CsvError::Overflow)?;
    }
    Ok(total)
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
    let mut parts = line.splitn(4, ' ');
    let (date, time, level) = (parts.next()?, parts.next()?, parts.next()?);
    if date.is_empty() || time.is_empty() || level.is_empty() {
        return None;
    }
    let message = parts.next().unwrap_or("");
    let millis = message
        .rsplitn(2, ' ')
        .next()
        .and_then(|word| word.strip_suffix("ms"))
        .filter(|n| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()))
        .and_then(|n| n.parse().ok());
    Some(LogLine { date, time, level, message, millis })
}
