use std::fmt;

/// An amount of money in cents.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Money {
    pub cents: i64,
}

/// Login details. They get logged with {:?}.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Credentials {
    pub user: String,
    pub password: String,
}

// TODO: Display for Money.
