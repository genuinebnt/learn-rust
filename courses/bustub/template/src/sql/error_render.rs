//! Showing where in the SQL text an error is.

/// 1-based `(line, column)` of byte `offset` in `src`; the column counts characters. `offset` must be a character boundary at most `src.len()`.
pub fn line_col(src: &str, offset: usize) -> (usize, usize) {
    todo!("3d-c4: count newlines before the offset, then the characters since the last one")
}

/// The message, the source line, and carets under `len` bytes starting at `offset`.
pub fn render_error(src: &str, offset: usize, len: usize, msg: &str) -> String {
    todo!("3d-c4: the message, the line, and the caret line")
}
