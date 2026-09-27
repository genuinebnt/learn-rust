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
    let mut after_space = true;
    s.retain(|c| {
        let space = c.is_whitespace();
        let keep = !(space && after_space);
        after_space = space;
        keep
    });
    let end = s.trim_end().len();
    s.truncate(end);
}

/// Removes the first complete line from `buf` and returns it without its "\n" or "\r\n".
/// `None`, with `buf` unchanged, when `buf` holds no '\n' yet.
pub fn pop_line(buf: &mut String) -> Option<String> {
    let nl = buf.find('\n')?;
    let mut line: String = buf.drain(..nl).collect();
    if line.ends_with('\r') {
        line.pop();
    }
    Some(line)
}
