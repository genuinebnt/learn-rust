pub struct Editor {
    pub text: String,
    pub history: Vec<String>,
}

impl Editor {
    fn save_snapshot(&mut self, s: &str) {
        self.history.push(s.to_string());
    }

    /// Saves the current text, then appends `more`.
    pub fn append(&mut self, more: &str) {
        let before = &self.text;
        self.save_snapshot(before);
        self.text.push_str(more);
    }
}
