//! Integer operations that report overflow and division by zero as errors.

#[derive(Debug, PartialEq, Eq)]
pub enum IntOpError {
    Overflow,
    DivisionByZero,
}

pub fn checked_add_i32(a: i32, b: i32) -> Result<i32, IntOpError> {
    a.checked_add(b).ok_or(IntOpError::Overflow)
}

pub fn checked_neg_i32(a: i32) -> Result<i32, IntOpError> {
    a.checked_neg().ok_or(IntOpError::Overflow)
}

pub fn checked_abs_i32(a: i32) -> Result<i32, IntOpError> {
    a.checked_abs().ok_or(IntOpError::Overflow)
}

pub fn checked_div_i32(a: i32, b: i32) -> Result<i32, IntOpError> {
    if b == 0 {
        return Err(IntOpError::DivisionByZero);
    }
    // @begin 3a-c4
    a.checked_div(b).ok_or(IntOpError::Overflow)
    //~ Ok(a / b)
    // @end
}
