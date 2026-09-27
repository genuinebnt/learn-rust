pub struct Editor {
    pub text: String,
    pub history: Vec<String>,
}

impl Editor {
    /// Saves the current text, then appends `more`.
    pub fn append(&mut self, more: &str) {
        self.text.push_str(more);
        self.history.push(self.text.to_string());
    }
}
