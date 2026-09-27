pub struct Batcher {
    current: Option<Vec<u32>>,
    size: usize,
}

impl Batcher {
    pub fn new(size: usize) -> Self {
        Batcher { current: None, size }
    }

    pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
        let batch = self.current.get_or_insert_with(Vec::new);
        if batch.len() == self.size {
            let full = self.current.replace(vec![value]);
            return full;
        }
        batch.push(value);
        None
    }

    pub fn flush(&mut self) -> Option<Vec<u32>> {
        self.current.take()
    }
}
