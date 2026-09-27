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

    pub fn count_words_equal_to(&self, word: &str) -> usize {
        self.words.iter().filter(|w| *w == word).count()
    }

    pub fn count_words_starting_with(&self, prefix: &str) -> usize {
        self.words.iter().filter(|w| w.starts_with(prefix)).count()
    }

    pub fn erase(&mut self, word: &str) -> bool {
        match self.words.iter().position(|w| w == word) {
            Some(i) => {
                self.words.swap_remove(i);
                true
            }
            None => false,
        }
    }
}
