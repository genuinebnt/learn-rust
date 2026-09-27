/// Words of `text` longer than `min` characters, as owned Strings.
pub fn long_words(text: &str, min: usize) -> impl Iterator<Item = String> {
    text.split_whitespace().filter(move |w| w.chars().count() > min).map(String::from)
}
