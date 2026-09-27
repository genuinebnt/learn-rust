pub struct StreamChecker {
    words: Vec<String>,
    stream: String,
}

impl StreamChecker {
    pub fn new(words: &[&str]) -> Self {
        StreamChecker { words: words.iter().map(|w| w.to_string()).collect(), stream: String::new() }
    }

    pub fn query(&mut self, letter: char) -> bool {
        self.stream.push(letter);
        self.words.iter().any(|w| self.stream.ends_with(w.as_str()))
    }
}
