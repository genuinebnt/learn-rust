#[derive(Default)]
pub struct MinStack {
    items: Vec<(i32, i32)>,
}

impl MinStack {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, x: i32) {
        self.items.push((x, x));
    }

    pub fn pop(&mut self) -> Option<i32> {
        self.items.pop().map(|(x, _)| x)
    }

    pub fn top(&self) -> Option<i32> {
        self.items.last().map(|&(x, _)| x)
    }

    pub fn min(&self) -> Option<i32> {
        self.items.iter().map(|&(x, _)| x).min()
    }
}
