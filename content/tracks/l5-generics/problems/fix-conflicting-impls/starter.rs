use std::fmt;

pub trait Describe {
    fn describe(&self) -> String;
}

/// A user name, shown in lowercase.
pub struct Name(pub String);

impl fmt::Display for Name {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.0.to_lowercase())
    }
}

/// Anything printable describes itself with its Display text.
impl<T: fmt::Display> Describe for T {
    fn describe(&self) -> String {
        self.to_string()
    }
}

/// `[a, b, c]`
impl<T: Describe> Describe for Vec<T> {
    fn describe(&self) -> String {
        let parts: Vec<String> = self.iter().map(|x| x.describe()).collect();
        format!("[{}]", parts.join(", "))
    }
}

/// The value, or `-` for None.
impl<T: Describe> Describe for Option<T> {
    fn describe(&self) -> String {
        match self {
            Some(x) => x.describe(),
            None => "-".to_string(),
        }
    }
}
