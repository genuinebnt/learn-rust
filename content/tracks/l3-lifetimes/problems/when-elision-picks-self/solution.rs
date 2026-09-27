pub struct Config {
    name: String,
    tags: Vec<String>,
}

impl Config {
    pub fn new(name: &str, tags: &[&str]) -> Self {
        Config { name: name.to_string(), tags: tags.iter().map(|t| t.to_string()).collect() }
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    /// The first tag that starts with `prefix`.
    pub fn tag_with_prefix(&self, prefix: &str) -> Option<&str> {
        self.tags.iter().map(String::as_str).find(|t| t.starts_with(prefix))
    }
}
