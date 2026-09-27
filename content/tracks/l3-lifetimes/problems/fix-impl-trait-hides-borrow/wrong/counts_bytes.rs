/// Words of `text` longer than `min` characters, as owned Strings.
pub fn long_words(text: &str, min: usize) -> impl Iterator<Item = String> + '_ {
    text.split_whitespace().filter(move |w| w.len() > min).map(String::from)
}
