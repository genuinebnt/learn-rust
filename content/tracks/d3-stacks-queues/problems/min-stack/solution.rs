/// Each entry stores the value and the minimum of everything at or below it.
#[derive(Default)]
pub struct MinStack {
    items: Vec<(i32, i32)>,
}

impl MinStack {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, x: i32) {
        let min = self.min().map_or(x, |m| m.min(x));
        self.items.push((x, min));
    }

    pub fn pop(&mut self) -> Option<i32> {
        self.items.pop().map(|(x, _)| x)
    }

    pub fn top(&self) -> Option<i32> {
        self.items.last().map(|&(x, _)| x)
    }

    pub fn min(&self) -> Option<i32> {
        self.items.last().map(|&(_, m)| m)
    }
}
