/// The extension of the last path component: "src/a.tar.gz" → Some("gz").
/// A leading dot is part of the name (".bashrc" has none), and so is a trailing one ("notes." has none).
pub fn extension(path: &str) -> Option<&str> {
    let name = path.rsplit_once('/').map_or(path, |(_, name)| name);
    let (stem, ext) = name.rsplit_once('.')?;
    (!stem.is_empty() && !ext.is_empty()).then_some(ext)
}

/// `s` without one pair of matching surrounding quotes, `"…"` or `'…'`; otherwise `s` unchanged.
pub fn unquote(s: &str) -> &str {
    let b = s.as_bytes();
    if !b.is_empty() && (b[0] == b'"' || b[0] == b'\'') && b[b.len() - 1] == b[0] {
        return &s[1..s.len() - 1];
    }
    s
}

/// Adds `key=value` to the query of `url`, in place. A `#fragment` stays at the end.
pub fn add_param(url: &mut String, key: &str, value: &str) {
    let end = url.find('#').unwrap_or(url.len());
    let head = &url[..end];
    let sep = if !head.contains('?') {
        "?"
    } else if head.ends_with(['?', '&']) {
        ""
    } else {
        "&"
    };
    url.reserve(sep.len() + key.len() + 1 + value.len());
    let mut at = end;
    for piece in [sep, key, "=", value] {
        url.insert_str(at, piece);
        at += piece.len();
    }
}
