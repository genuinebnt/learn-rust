/// Clears `words` and returns the length of the longest one (0 if empty).
pub fn longest_then_clear(words: &mut Vec<String>) -> usize {
    let longest = words.len();
    words.clear();
    longest
}
