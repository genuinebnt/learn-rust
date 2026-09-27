use std::str::FromStr;

#[derive(Debug, PartialEq)]
pub struct Setting {
    pub key: String,
    pub value: i64,
}

#[derive(Debug, PartialEq)]
pub enum SettingError {
    MissingEquals,
    EmptyKey,
    BadValue(String),
}

impl FromStr for Setting {
    type Err = SettingError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let (key, raw) = s.split_once('=').ok_or(SettingError::MissingEquals)?;
        let key = key.trim();
        if key.is_empty() {
            return Err(SettingError::EmptyKey);
        }
        let value = raw.trim().parse().map_err(|_| SettingError::BadValue(raw.to_string()))?;
        Ok(Setting { key: key.to_string(), value })
    }
}
