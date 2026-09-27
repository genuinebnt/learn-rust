/// A combining diacritical mark (U+0300..=U+036F).
fn is_mark(c: char) -> bool {
    matches!(c, '\u{300}'..='\u{36f}')
}

pub fn reverse_each_word(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut rest = s;
    while !rest.is_empty() {
        let body = rest.trim_start();
        out.push_str(&rest[..rest.len() - body.len()]);
        let end = body.find(char::is_whitespace).unwrap_or(body.len());
        let (word, tail) = body.split_at(end);
        let mut cut = word.len();
        for (i, c) in word.char_indices().rev() {
            if !word[..i].ends_with(is_mark) || i == 0 {
                out.push_str(&word[i..cut]);
                cut = i;
            }
        }
        rest = tail;
    }
    out
}
