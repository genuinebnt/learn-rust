use std::borrow::Cow;

/// `s` with `&`, `<`, `>`, `"` and `'` escaped. Borrows `s` when there's nothing to escape.
pub fn escape_html(s: &str) -> Cow<'_, str> {
    if !s.contains(['&', '<', '>', '"', '\'']) {
        return Cow::Borrowed(s);
    }
    Cow::Owned(s.replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;").replace('\'', "&#39;").replace('&', "&amp;"))
}

/// `bytes` decoded as UTF-8 (each invalid sequence becomes U+FFFD), then escaped like `escape_html`.
/// Borrows when nothing was replaced or escaped, and never copies the text more than it must.
pub fn escape_bytes(bytes: &[u8]) -> Cow<'_, str> {
    match String::from_utf8_lossy(bytes) {
        Cow::Borrowed(text) => escape_html(text),
        Cow::Owned(text) => match escape_html(&text) {
            Cow::Borrowed(_) => Cow::Owned(text),
            Cow::Owned(escaped) => Cow::Owned(escaped),
        },
    }
}
