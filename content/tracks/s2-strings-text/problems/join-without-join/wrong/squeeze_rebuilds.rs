/// `words` joined by `sep`, in one allocation of exactly the final size.
pub fn join_words(words: &[&str], sep: &str) -> String {
    let len = words.iter().map(|w| w.len()).sum::<usize>() + sep.len() * words.len().saturating_sub(1);
    let mut out = String::with_capacity(len);
    for (i, w) in words.iter().enumerate() {
        if i > 0 {
            out.push_str(sep);
        }
        out.push_str(w);
    }
    out
}

/// Drops leading and trailing whitespace, and in each inner run of whitespace keeps only its first
/// character. In place, no allocation.
pub fn squeeze(s: &mut String) {
    let mut out = String::with_capacity(s.len());
    let mut after_space = true;
    for c in s.chars() {
        if !(c.is_whitespace() && after_space) {
            out.push(c);
        }
        after_space = c.is_whitespace();
    }
    let end = out.trim_end().len();
    out.truncate(end);
    *s = out;
}

/// Removes the first complete line from `buf` and returns it without its "\n" or "\r\n".
/// `None`, with `buf` unchanged, when `buf` holds no '\n' yet.
pub fn pop_line(buf: &mut String) -> Option<String> {
    let nl = buf.find('\n')?;
    let mut line: String = buf.drain(..=nl).collect();
    line.pop();
    if line.ends_with('\r') {
        line.pop();
    }
    Some(line)
}
