use std::num::{ParseFloatError, ParseIntError};

#[derive(Debug, PartialEq)]
pub enum SizeError {
    Missing(&'static str),
    BadInt(ParseIntError),
    BadFloat(ParseFloatError),
}

impl From<ParseIntError> for SizeError {
    fn from(e: ParseIntError) -> Self {
        SizeError::BadInt(e)
    }
}

impl From<ParseFloatError> for SizeError {
    fn from(e: ParseFloatError) -> Self {
        SizeError::BadFloat(e)
    }
}

fn field<'a>(s: &'a str, name: &'static str) -> Result<&'a str, SizeError> {
    s.split(';')
        .find_map(|kv| kv.strip_prefix(name)?.strip_prefix('='))
        .ok_or(SizeError::Missing(name))
}

/// Parses "width=80;height=24;scale=1.5" into (80, 24, 1.5). The scale is optional and defaults to 1.0.
pub fn size(s: &str) -> Result<(u32, u32, f64), SizeError> {
    let w = field(s, "width")?.parse::<u32>()?;
    let h = field(s, "height")?.parse::<u32>()?;
    let scale = match field(s, "scale") {
        Ok(v) => v.parse::<f64>()?,
        Err(_) => 1.0,
    };
    Ok((w, h, scale))
}
