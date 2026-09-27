/// One CSV field. A field that contains a comma, a double quote, `\r` or `\n` is wrapped in double
/// quotes, with each inner double quote doubled. Any other field is written as it is.
pub fn csv_field(s: &str) -> String {
    if s.contains([',', '"', '\r', '\n']) {
        format!("\"{}\"", s.replace('"', "\"\""))
    } else {
        s.to_string()
    }
}

/// The fields as one CSV row, separated by commas.
pub fn csv_row(fields: &[&str]) -> String {
    let mut row = String::new();
    for f in fields {
        if !row.is_empty() {
            row.push(',');
        }
        row += &csv_field(f);
    }
    row
}
