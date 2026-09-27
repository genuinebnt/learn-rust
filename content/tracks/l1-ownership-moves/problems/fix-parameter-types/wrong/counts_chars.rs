/// How many words are at least `min` bytes long.
pub fn count_long(words: &[String], min: usize) -> usize {
    words.iter().filter(|w| w.chars().count() >= min).count()
}

/// Uppercases every word in place.
pub fn shout_all(words: &mut [String]) {
    for w in words.iter_mut() {
        w.make_ascii_uppercase();
    }
}

/// Joins the words with spaces.
pub fn into_sentence(words: Vec<String>) -> String {
    words.join(" ")
}
