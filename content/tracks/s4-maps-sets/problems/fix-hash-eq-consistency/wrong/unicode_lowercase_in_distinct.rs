use std::collections::HashSet;
use std::hash::{Hash, Hasher};

/// A username that compares case-insensitively.
#[derive(Debug, Clone)]
pub struct Username(pub String);

impl PartialEq for Username {
    fn eq(&self, other: &Self) -> bool {
        self.0.eq_ignore_ascii_case(&other.0)
    }
}

impl Eq for Username {}

impl Hash for Username {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.0.to_ascii_lowercase().hash(state);
    }
}

/// How many different usernames there are, ignoring case.
pub fn distinct(names: &[&str]) -> usize {
    names.iter().map(|n| n.to_lowercase()).collect::<HashSet<_>>().len()
}
