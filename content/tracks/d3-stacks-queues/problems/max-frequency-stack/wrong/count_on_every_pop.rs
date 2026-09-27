use std::collections::HashMap;

#[derive(Default)]
pub struct FreqStack {
    items: Vec<i32>,
}

impl FreqStack {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, x: i32) {
        self.items.push(x);
    }

    pub fn pop(&mut self) -> Option<i32> {
        let mut freq: HashMap<i32, usize> = HashMap::new();
        for &x in &self.items {
            *freq.entry(x).or_insert(0) += 1;
        }
        let best = *freq.values().max()?;
        let i = self.items.iter().rposition(|x| freq[x] == best)?;
        Some(self.items.remove(i))
    }
}
