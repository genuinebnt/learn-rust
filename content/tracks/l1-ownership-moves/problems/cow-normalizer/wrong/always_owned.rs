use std::borrow::Cow;

pub fn normalize(s: &str) -> Cow<'_, str> {
    Cow::Owned(s.replace('\t', "    "))
}
