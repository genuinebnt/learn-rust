use std::collections::HashMap;

#[derive(Default)]
pub struct FreqStack {
    freq: HashMap<i32, usize>,
    /// groups[f - 1]: elements that reached frequency f, in push order.
    groups: Vec<Vec<i32>>,
}

impl FreqStack {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, x: i32) {
        todo!()
    }

    pub fn pop(&mut self) -> Option<i32> {
        todo!()
    }
}
