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

    fn shift(&mut self) {
        self.outbox.extend(self.inbox.drain(..).rev());
    }

    fn unshift(&mut self) {

    }

    pub fn pop(&mut self) -> Option<i32> {
        self.shift();
        let x = self.outbox.pop();
        self.unshift();
        x
    }

    pub fn peek(&mut self) -> Option<i32> {
        self.shift();
        let x = self.outbox.last().copied();
        self.unshift();
        x
    }

    pub fn len(&self) -> usize {
        self.inbox.len() + self.outbox.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}
