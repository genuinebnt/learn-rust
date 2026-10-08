//! Port of `src/include/common/exception.h`: BusTub's exceptions. C++ throws; Rust returns `Result<_, Exception>` (a failing
//! SQL operation such as an overflow, a division by zero or an impossible cast is an *expected* error, not a bug). Given code.

use std::fmt;

/// BusTub's `ExceptionType` (the kinds this port uses).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ExceptionType {
    Invalid,
    OutOfRange,
    Conversion,
    UnknownType,
    Decimal,
    MismatchType,
    DivideByZero,
    IncompatibleType,
    NotImplemented,
    Execution,
    Optimizer,
    Io,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Exception {
    pub kind: ExceptionType,
    pub message: String,
}

impl Exception {
    pub fn new(kind: ExceptionType, message: impl Into<String>) -> Exception {
        Exception { kind, message: message.into() }
    }
}

impl fmt::Display for Exception {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Exception: [{:?}] {}", self.kind, self.message)
    }
}

impl std::error::Error for Exception {}

pub type Result<T> = std::result::Result<T, Exception>;
