use std::cmp::Ordering;

/// Natural order: runs of ASCII digits compare by numeric value, everything else char by char.
/// Strings that tie compare as plain strings, so the order is total.
pub fn natural_cmp(a: &str, b: &str) -> Ordering {
    todo!()
}

/// The Luhn check: spaces are ignored, anything else must be an ASCII digit, and there must be at
/// least two digits.
pub fn luhn_valid(s: &str) -> bool {
    todo!()
}
