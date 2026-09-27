use std::borrow::Cow;

pub fn normalize(s: &str) -> Cow<'_, str> {
    if !s.contains('\t') {
        return Cow::Borrowed(s);
    }
    let mut out = s.to_string();
    while let Some(i) = out.find('\t') {
        out.replace_range(i..i + 1, "    ");
    }
    Cow::Owned(out)
}
