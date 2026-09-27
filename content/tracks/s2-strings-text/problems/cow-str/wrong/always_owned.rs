use std::borrow::Cow;

pub fn escape_html(s: &str) -> Cow<'_, str> {
    Cow::Owned(s.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;").replace('\'', "&#39;"))
}
