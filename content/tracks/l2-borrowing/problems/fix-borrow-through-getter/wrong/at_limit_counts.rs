pub struct Shop {
    items: Vec<u32>,
    log: Vec<String>,
}

impl Shop {
    pub fn new(items: Vec<u32>) -> Self {
        Shop { items, log: Vec::new() }
    }

    /// Logs every price above `limit`.
    pub fn log_expensive(&mut self, limit: u32) {
        for p in &self.items {
            if *p >= limit {
                self.log.push(format!("expensive: {p}"));
            }
        }
    }

    pub fn log(&self) -> &[String] {
        &self.log
    }
}
