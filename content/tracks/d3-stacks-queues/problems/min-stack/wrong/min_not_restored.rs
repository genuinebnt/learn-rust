#[derive(Default)]
pub struct MinStack {
    items: Vec<i32>,
    min: Option<i32>,
}

impl MinStack {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, x: i32) {
        self.items.push(x);
        self.min = Some(self.min.map_or(x, |m| m.min(x)));
    }

    pub fn pop(&mut self) -> Option<i32> {
        let x = self.items.pop();
        if self.items.is_empty() {
            self.min = None;
        }
        x
    }

    pub fn top(&self) -> Option<i32> {
        self.items.last().copied()
    }

    pub fn min(&self) -> Option<i32> {
        self.min
    }
}
