use std::borrow::Cow;

pub fn escape_html(s: &str) -> Cow<'_, str> {
    let special = |c: char| matches!(c, '&' | '<' | '>' | '"' | '\'');
    let Some(first) = s.find(special) else {
        return Cow::Borrowed(s);
    };
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
