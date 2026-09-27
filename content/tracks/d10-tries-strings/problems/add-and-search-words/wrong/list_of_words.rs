#[derive(Default)]
pub struct WordDictionary {
    words: Vec<String>,
}

impl WordDictionary {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add_word(&mut self, word: &str) {
        self.words.push(word.to_string());
    }

    pub fn search(&self, pattern: &str) -> bool {
        self.words.iter().any(|w| w.len() == pattern.len() && w.bytes().zip(pattern.bytes()).all(|(a, b)| b == b'.' || a == b))
    }
}
