/// The extension of the last path component: "src/a.tar.gz" → Some("gz").
/// A leading dot is part of the name (".bashrc" has none), and so is a trailing one ("notes." has none).
pub fn extension(path: &str) -> Option<&str> {
    let name = path;
    let (stem, ext) = name.rsplit_once('.')?;
    (!stem.is_empty() && !ext.is_empty()).then_some(ext)
}

/// `s` without one pair of matching surrounding quotes, `"…"` or `'…'`; otherwise `s` unchanged.
pub fn unquote(s: &str) -> &str {
    for q in ['"', '\''] {
        if let Some(inner) = s.strip_prefix(q).and_then(|rest| rest.strip_suffix(q)) {
            return inner;
        }
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
