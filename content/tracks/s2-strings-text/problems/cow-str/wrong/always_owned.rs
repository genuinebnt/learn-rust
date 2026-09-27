use std::borrow::Cow;

/// `s` with `&`, `<`, `>`, `"` and `'` escaped. Borrows `s` when there's nothing to escape.
pub fn escape_html(s: &str) -> Cow<'_, str> {
    let special = |c: char| matches!(c, '&' | '<' | '>' | '"' | '\'');
    let first = s.find(special).unwrap_or(s.len());
    let mut out = String::with_capacity(s.len() + 8);
    out.push_str(&s[..first]);
    for c in s[first..].chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&#39;"),
            _ => out.push(c),
        }
    }
    Cow::Owned(out)
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
