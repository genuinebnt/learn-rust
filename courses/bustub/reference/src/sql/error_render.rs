//! Showing where in the SQL text an error is.

/// 1-based `(line, column)` of byte `offset` in `src`; the column counts characters. `offset` must be a character boundary at most `src.len()`.
pub fn line_col(src: &str, offset: usize) -> (usize, usize) {
    // @begin 3d-c4
    let before = &src[..offset];
    let line = before.matches('\n').count() + 1;
    let line_start = before.rfind('\n').map_or(0, |i| i + 1);
    (line, src[line_start..offset].chars().count() + 1)
    //~ todo!("3d-c4: count newlines before the offset, then the characters since the last one")
    // @end
}

/// The message, the source line, and carets under `len` bytes starting at `offset`.
pub fn render_error(src: &str, offset: usize, len: usize, msg: &str) -> String {
    // @begin 3d-c4
    let (line_no, col) = line_col(src, offset);
    let line_start = src[..offset].rfind('\n').map_or(0, |i| i + 1);
    let line_end = src[offset..].find('\n').map_or(src.len(), |i| offset + i);
    let line = src[line_start..line_end].trim_end_matches('\r');
    let prefix = format!("LINE {line_no}: ");
    let width = (src[offset..(offset + len).min(line_end)].chars().count()).max(1);
    let carets = "^".repeat(width);
    format!("{msg}\n{prefix}{line}\n{}{}", " ".repeat(prefix.chars().count() + col - 1), carets)
    //~ todo!("3d-c4: the message, the line, and the caret line")
    // @end
}
