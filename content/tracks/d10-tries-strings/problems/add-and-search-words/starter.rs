#[derive(Default)]
pub struct WordDictionary {
    // your fields here
}

impl WordDictionary {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add_word(&mut self, word: &str) {
        todo!()
    }

    pub fn search(&self, pattern: &str) -> bool {
        todo!()
    }
}
