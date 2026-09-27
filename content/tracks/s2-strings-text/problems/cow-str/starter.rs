use std::borrow::Cow;

/// `s` with `&`, `<`, `>`, `"` and `'` escaped. Borrows `s` when there's nothing to escape.
pub fn escape_html(s: &str) -> Cow<'_, str> {
    todo!()
}

/// `bytes` decoded as UTF-8 (each invalid sequence becomes U+FFFD), then escaped like `escape_html`.
/// Borrows when nothing was replaced or escaped, and never copies the text more than it must.
pub fn escape_bytes(bytes: &[u8]) -> Cow<'_, str> {
    todo!()
}
