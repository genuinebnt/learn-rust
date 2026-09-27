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
        self.inbox.push(x);
    }

    /// Refill the outbox, reversed, only when it's empty: each element moves once.
    fn shift(&mut self) {
        if self.outbox.is_empty() {
            self.outbox.extend(self.inbox.drain(..).rev());
        }
    }

    pub fn pop(&mut self) -> Option<i32> {
        self.shift();
        self.outbox.pop()
    }

    /// The front element, without removing it.
    pub fn peek(&mut self) -> Option<i32> {
        self.shift();
        self.outbox.last().copied()
    }

    pub fn len(&self) -> usize {
        self.inbox.len() + self.outbox.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}
