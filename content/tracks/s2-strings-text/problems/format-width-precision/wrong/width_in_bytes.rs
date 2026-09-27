use std::fmt::Write;

/// One line per row, each ending in '\n': the name left-aligned and padded to the longest name, " | ",
/// then the value with `prec` decimals, right-aligned to the widest formatted value.
pub fn table(rows: &[(&str, f64)], prec: usize) -> String {
    let name_w = rows.iter().map(|(name, _)| name.len()).max().unwrap_or(0);
    let value_w = rows.iter().map(|(_, v)| format!("{v:.prec$}").len()).max().unwrap_or(0);
    let mut out = String::new();
    for (name, value) in rows {
        writeln!(out, "{name:<name_w$} | {value:>value_w$.prec$}").unwrap();
    }
    out
}

/// "0x" and 8 lowercase hex digits, " = ", then the 32 bits, most significant byte first, in four
/// groups of 8 joined by '_'.
pub fn register(value: u32) -> String {
    let [a, b, c, d] = value.to_be_bytes();
    format!("{value:#010x} = {a:08b}_{b:08b}_{c:08b}_{d:08b}")
}

/// One `hexdump -C` line for up to 16 bytes starting at `offset`.
pub fn hexdump_line(offset: usize, bytes: &[u8]) -> String {
    let mut hex = String::with_capacity(49);
    for (i, b) in bytes.iter().enumerate() {
        write!(hex, "{b:02x} ").unwrap();
        if i == 7 {
            hex.push(' ');
        }
    }
    let ascii: String = bytes.iter().map(|&b| if b.is_ascii_graphic() || b == b' ' { b as char } else { '.' }).collect();
    format!("{offset:08x}  {hex:<49} |{ascii}|")
}
