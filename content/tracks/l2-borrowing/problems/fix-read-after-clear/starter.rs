/// Clears `words` and returns the length of the longest one (0 if empty).
pub fn longest_then_clear(words: &mut Vec<String>) -> usize {
    let longest = words.iter().max_by_key(|w| w.len());
    words.clear();
    longest.map_or(0, |w| w.len())
}
