pub struct Splitter<'t, 's> {
    text: &'t str,
    sep: &'s str,
}

impl<'t, 's> Splitter<'t, 's> {
    pub fn new(text: &'t str, sep: &'s str) -> Self {
        Splitter { text, sep }
    }

    pub fn first(&self) -> &'t str {
        self.text.split(self.sep).next().unwrap_or("")
    }

    pub fn parts(&self) -> Vec<&'t str> {
        self.text.split_terminator(self.sep).collect()
    }
}
