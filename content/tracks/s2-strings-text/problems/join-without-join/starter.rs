/// `words` joined by `sep`, in one allocation of exactly the final size.
pub fn join_words(words: &[&str], sep: &str) -> String {
    todo!()
}

/// Drops leading and trailing whitespace, and in each inner run of whitespace keeps only its first
/// character. In place, no allocation.
pub fn squeeze(s: &mut String) {
    todo!()
}

/// Removes the first complete line from `buf` and returns it without its "\n" or "\r\n".
/// `None`, with `buf` unchanged, when `buf` holds no '\n' yet.
pub fn pop_line(buf: &mut String) -> Option<String> {
    todo!()
}
