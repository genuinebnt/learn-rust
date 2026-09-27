#[derive(Default)]
pub struct TwoStackQueue {
    inbox: Vec<i32>,
    outbox: Vec<i32>,
}

impl TwoStackQueue {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, x: i32) {
        todo!()
    }

    pub fn pop(&mut self) -> Option<i32> {
        todo!()
    }

    /// The front element, without removing it.
    pub fn peek(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn is_empty(&self) -> bool {
        todo!()
    }
}
