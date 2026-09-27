use std::error::Error;
use std::fmt;

#[derive(Debug)]
pub struct ConfigError {
    pub line: usize,
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "line {}: expected key=value", self.line)
    }
}

impl Error for ConfigError {}

pub fn sum_config(text: &str) -> Result<i64, Box<dyn Error>> {
    let mut total = 0;
    for (i, line) in text.lines().enumerate() {
        if line.trim().is_empty() {
            continue;
        }
        let (_, value) = line.rsplit_once('=').ok_or(ConfigError { line: i + 1 })?;
        total += value.trim().parse::<i64>()?;
    }
    Ok(total)
}

pub fn bad_line(err: &(dyn Error + 'static)) -> Option<usize> {
    err.downcast_ref::<ConfigError>().map(|e| e.line)
}
