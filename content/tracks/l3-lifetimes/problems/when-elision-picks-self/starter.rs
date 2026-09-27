pub struct Config {
    name: String,
    tags: Vec<String>,
}

impl Config {
    pub fn new(name: &str, tags: &[&str]) -> Self {
        todo!()
    }

    pub fn name(&self) -> &str {
        todo!()
    }

    /// The first tag that starts with `prefix`.
    pub fn tag_with_prefix(&self, prefix: &str) -> Option<&str> {
        todo!()
    }
}
