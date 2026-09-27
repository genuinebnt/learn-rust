/// How many words are at least `min` bytes long.
pub fn count_long(words: Vec<String>, min: usize) -> usize {
    words.iter().filter(|w| w.len() >= min).count()
}

/// Uppercases every word in place.
pub fn shout_all(mut words: Vec<String>) {
    for w in words.iter_mut() {
        w.make_ascii_uppercase();
    }
}

/// Joins the words with spaces.
pub fn into_sentence(words: Vec<String>) -> String {
    words.join(" ")
}
