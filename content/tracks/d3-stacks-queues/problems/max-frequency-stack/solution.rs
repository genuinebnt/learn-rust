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
        let f = self.freq.entry(x).or_insert(0);
        *f += 1;
        if *f > self.groups.len() {
            self.groups.push(Vec::new());
        }
        self.groups[*f - 1].push(x);
    }

    pub fn pop(&mut self) -> Option<i32> {
        let top = self.groups.last_mut()?;
        let x = top.pop()?;
        if top.is_empty() {
            self.groups.pop();
        }
        match self.freq.get_mut(&x) {
            Some(f) if *f > 1 => *f -= 1,
            _ => {
                self.freq.remove(&x);
            }
        }
        Some(x)
    }
}
