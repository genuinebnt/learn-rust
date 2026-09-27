use std::fmt::Write;

/// One line per row, each ending in '\n': the name left-aligned and padded to the longest name, " | ",
/// then the value with `prec` decimals, right-aligned to the widest formatted value.
pub fn table(rows: &[(&str, f64)], prec: usize) -> String {
    todo!()
}

/// "0x" and 8 lowercase hex digits, " = ", then the 32 bits, most significant byte first, in four
/// groups of 8 joined by '_'.
pub fn register(value: u32) -> String {
    todo!()
}

/// One `hexdump -C` line for up to 16 bytes starting at `offset`.
pub fn hexdump_line(offset: usize, bytes: &[u8]) -> String {
    todo!()
}
