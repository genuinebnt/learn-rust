pub struct Library {
    books: Vec<String>,
}

impl Library {
    pub fn new(books: Vec<String>) -> Self {
        Library { books }
    }

    /// Titles containing `needle`.
    pub fn search(&self, needle: &str) -> Vec<&str> {
        self.books.iter().filter(|b| b.contains(needle)).map(String::as_str).collect()
    }

    /// The longest title; the last one on a tie.
    pub fn longest(&self) -> Option<&str> {
        let mut best: Option<&str> = None;
        for b in &self.books {
            if best.map_or(true, |l| b.len() > l.len()) {
                best = Some(b);
            }
        }
        best
    }

    pub fn count_with(&self, needle: &str) -> usize {
        self.books.iter().filter(|b| b.contains(needle)).count()
    }
}
