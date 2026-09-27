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
        self
    }
}

/// Prints as `(first, second)`.
impl<T: fmt::Display> fmt::Display for Pair<T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.first, self.second)
    }
}
