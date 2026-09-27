/// How many words are at least `min` bytes long.
pub fn count_long(words: Vec<String>, min: usize) -> usize {
    words.iter().filter(|w| w.len() >= min).count()
}

/// The longest word, borrowed; the last of the longest on a tie.
pub fn longest(words: Vec<String>) -> Option<String> {
    words.into_iter().max_by_key(|w| w.len())
}

/// Uppercases every word in place.
pub fn shout_all(mut words: Vec<String>) {
    for w in words.iter_mut() {
        w.make_ascii_uppercase();
    }
}

/// Removes the words shorter than `min` bytes, keeping the order of the rest.
pub fn drop_short(mut words: Vec<String>, min: usize) {
    words.retain(|w| w.len() >= min);
}

/// Joins the words with spaces.
pub fn into_sentence(words: Vec<String>) -> String {
    words.join(" ")
}
