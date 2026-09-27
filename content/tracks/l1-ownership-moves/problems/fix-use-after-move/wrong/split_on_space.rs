/// The number of words and the longest word, e.g. "the quick fox" → (3, "quick").
pub fn summarize(text: &str) -> (usize, String) {
    let words: Vec<String> = text.split_whitespace().map(String::from).collect();
    let count = text.split(' ').count();
    let longest = longest_word(words);
    (count, longest)
}

fn longest_word(words: Vec<String>) -> String {
    words.into_iter().fold(String::new(), |best, w| if w.len() > best.len() { w } else { best })
}
