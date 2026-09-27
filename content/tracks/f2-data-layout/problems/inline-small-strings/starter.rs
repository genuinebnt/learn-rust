use std::borrow::Borrow;
use std::cmp::Ordering;
use std::fmt;
use std::hash::{Hash, Hasher};
use std::ops::Deref;

/// An immutable string for a column of mostly short values (country codes, user names, enum-like tags).
#[derive(Clone)]
pub struct SmallStr {
    // Replace this: a `String` allocates for every non-empty value.
    s: String,
}

impl SmallStr {
    /// The longest string kept inline, in bytes.
    pub const INLINE_CAP: usize = 22;

    pub fn new(s: &str) -> SmallStr {
        todo!()
    }

    pub fn as_str(&self) -> &str {
        todo!()
    }

    /// Whether the bytes live inside the value rather than on the heap.
    pub fn is_inline(&self) -> bool {
        todo!()
    }
}

impl PartialEq for SmallStr {
    fn eq(&self, other: &SmallStr) -> bool {
        todo!()
    }
}

impl Eq for SmallStr {}

impl Hash for SmallStr {
    fn hash<H: Hasher>(&self, state: &mut H) {
        todo!()
    }
}

impl Ord for SmallStr {
    fn cmp(&self, other: &SmallStr) -> Ordering {
        todo!()
    }
}

/// Prints like a `&str`: `"abc"`.
impl fmt::Debug for SmallStr {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        todo!()
    }
}

impl fmt::Display for SmallStr {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        todo!()
    }
}

impl Deref for SmallStr {
    type Target = str;
    fn deref(&self) -> &str {
        self.as_str()
    }
}

impl Borrow<str> for SmallStr {
    fn borrow(&self) -> &str {
        self.as_str()
    }
}

impl From<&str> for SmallStr {
    fn from(s: &str) -> SmallStr {
        SmallStr::new(s)
    }
}

impl PartialOrd for SmallStr {
    fn partial_cmp(&self, other: &SmallStr) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
