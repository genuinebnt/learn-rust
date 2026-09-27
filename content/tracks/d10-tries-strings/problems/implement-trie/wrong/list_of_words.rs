#[derive(Default)]
pub struct Trie {
    words: Vec<String>,
}

impl Trie {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn insert(&mut self, word: &str) {
        self.words.push(word.to_string());
    }

    pub fn search(&self, word: &str) -> bool {
        self.words.iter().any(|w| w == word)
    }

    pub fn starts_with(&self, prefix: &str) -> bool {
        prefix.is_empty() || self.words.iter().any(|w| w.starts_with(prefix))
    }
}
