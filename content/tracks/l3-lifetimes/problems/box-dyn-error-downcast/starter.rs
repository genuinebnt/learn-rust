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
    todo!()
}

pub fn bad_line(err: &(dyn Error + 'static)) -> Option<usize> {
    todo!()
}
