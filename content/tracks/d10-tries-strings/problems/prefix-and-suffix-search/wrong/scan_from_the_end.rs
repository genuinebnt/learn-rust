pub struct WordFilter {
    words: Vec<String>,
}

impl WordFilter {
    pub fn new(words: &[&str]) -> Self {
        WordFilter { words: words.iter().map(|w| w.to_string()).collect() }
    }

    pub fn f(&self, prefix: &str, suffix: &str) -> Option<usize> {
        self.words.iter().rposition(|w| w.starts_with(prefix) && w.ends_with(suffix))
    }
}
