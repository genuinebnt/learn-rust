pub struct Batcher {
    current: Option<Vec<u32>>,
    size: usize,
}

impl Batcher {
    pub fn new(size: usize) -> Self {
        todo!()
    }

    pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
        todo!()
    }

    pub fn flush(&mut self) -> Option<Vec<u32>> {
        todo!()
    }
}
