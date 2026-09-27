/// The character at position `i` (in characters), or `None` past the end.
pub fn nth_letter(word: &str, i: usize) -> Option<char> {
    word.chars().nth(i)
}
