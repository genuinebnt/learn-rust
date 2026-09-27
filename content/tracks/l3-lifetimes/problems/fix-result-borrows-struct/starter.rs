pub struct Document<'a> {
    text: &'a str,
}

impl<'a> Document<'a> {
    pub fn new(text: &'a str) -> Self {
        Document { text }
    }

    /// The longest line; the first one on a tie.
    pub fn longest_line(&self) -> &str {
        self.text.lines().fold("", |best, l| if l.len() > best.len() { l } else { best })
    }

    /// Every line containing `word`.
    pub fn lines_with(&self, word: &str) -> Vec<&str> {
        self.text.lines().filter(|l| l.contains(word)).collect()
    }
}
