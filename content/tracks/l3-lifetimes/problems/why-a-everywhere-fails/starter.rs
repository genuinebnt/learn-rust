pub struct Splitter<'a> {
    text: &'a str,
    sep: &'a str,
}

impl<'a> Splitter<'a> {
    pub fn new(text: &'a str, sep: &'a str) -> Self {
        Splitter { text, sep }
    }

    pub fn first(&self) -> &'a str {
        self.text.split(self.sep).next().unwrap_or("")
    }

    pub fn parts(&self) -> Vec<&'a str> {
        self.text.split(self.sep).collect()
    }
}
