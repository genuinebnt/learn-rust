use std::fmt;

/// Two values of the same type.
#[derive(Debug, PartialEq)]
pub struct Pair<T> {
    pub first: T,
    pub second: T,
}

impl<T> Pair<T> {
    pub fn new(first: T, second: T) -> Self {
        Pair { first, second }
    }

    /// The same pair with its halves exchanged.
    pub fn swap(self) -> Pair<T> {
        Pair { first: self.second, second: self.first }
    }
}

/// Prints as `(first, second)`.
impl<T> fmt::Display for Pair<T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.first, self.second)
    }
}
