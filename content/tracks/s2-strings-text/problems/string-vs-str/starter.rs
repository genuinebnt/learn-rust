/// The extension of the last path component: "src/a.tar.gz" → Some("gz").
/// A leading dot is part of the name (".bashrc" has none), and so is a trailing one ("notes." has none).
pub fn extension(path: &str) -> Option<&str> {
    todo!()
}

/// `s` without one pair of matching surrounding quotes, `"…"` or `'…'`; otherwise `s` unchanged.
pub fn unquote(s: &str) -> &str {
    todo!()
}

/// Adds `key=value` to the query of `url`, in place. A `#fragment` stays at the end.
pub fn add_param(url: &mut String, key: &str, value: &str) {
    todo!()
}
