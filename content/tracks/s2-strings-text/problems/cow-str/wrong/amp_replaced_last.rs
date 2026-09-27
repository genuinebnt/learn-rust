use std::borrow::Cow;

pub fn escape_html(s: &str) -> Cow<'_, str> {
    if !s.contains(['&', '<', '>', '"', '\'']) {
        return Cow::Borrowed(s);
    }
    Cow::Owned(s.replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;").replace('\'', "&#39;").replace('&', "&amp;"))
}
