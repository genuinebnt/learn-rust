use std::collections::HashMap;

/// The `k` most frequent words of `text` with their counts, most frequent first; a tie goes to the word that
/// appeared first. A word is a maximal run of alphanumeric chars (`char::is_alphanumeric`). Words that differ
/// only in ASCII case are the same word, reported with the spelling it first appeared with, as a slice of `text`.
pub fn top_words(text: &str, k: usize) -> Vec<(&str, usize)> {
    todo!()
}
