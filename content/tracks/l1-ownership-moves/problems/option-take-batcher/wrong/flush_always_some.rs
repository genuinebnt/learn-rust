pub struct Batcher {
    current: Vec<u32>,
    size: usize,
}

impl Batcher {
    pub fn new(size: usize) -> Self {
        Batcher { current: Vec::new(), size }
    }

    pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
        self.current.push(value);
        if self.current.len() == self.size {
            Some(std::mem::take(&mut self.current))
        } else {
            None
        }
    }

    pub fn flush(&mut self) -> Option<Vec<u32>> {
        Some(std::mem::take(&mut self.current))
    }
}
