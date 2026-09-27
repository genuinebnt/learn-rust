use std::borrow::Cow;

pub fn normalize(s: &str) -> Cow<'_, str> {
    if !s.contains('\t') {
        return Cow::Borrowed(s);
    }
    let mut out = String::new();
    let mut col = 0;
    for c in s.chars() {
        if c == '\t' {
            let pad = 4 - col % 4;
            out.push_str(&" ".repeat(pad));
            col += pad;
        } else {
            out.push(c);
            col += 1;
        }
    }
    Cow::Owned(out)
}
