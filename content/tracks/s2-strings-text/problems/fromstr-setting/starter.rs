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
        todo!()
    }
}
