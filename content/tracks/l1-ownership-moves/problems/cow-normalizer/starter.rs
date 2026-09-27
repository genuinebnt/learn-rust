use std::borrow::Cow;

/// Strips trailing whitespace and replaces each tab with four spaces. Borrows whenever no tab is left to
/// replace, even if the end was trimmed.
pub fn normalize(s: &str) -> Cow<'_, str> {
    todo!()
}

/// Ends `line` with a '\n'. A line that already has one comes back untouched; an owned line gets the
/// newline pushed onto its own buffer.
pub fn with_newline(line: Cow<'_, str>) -> Cow<'_, str> {
    todo!()
}
