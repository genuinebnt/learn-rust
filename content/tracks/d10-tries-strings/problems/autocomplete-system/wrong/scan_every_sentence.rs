use std::collections::HashMap;

pub struct AutocompleteSystem {
    counts: HashMap<String, u64>,
    typed: String,
}

impl AutocompleteSystem {
    pub fn new(sentences: &[&str], times: &[u32]) -> Self {
        let mut counts: HashMap<String, u64> = HashMap::new();
        for (s, &t) in sentences.iter().zip(times) {
            *counts.entry(s.to_string()).or_insert(0) += u64::from(t);
        }
        AutocompleteSystem { counts, typed: String::new() }
    }

    pub fn input(&mut self, c: char) -> Vec<String> {
        if c == '#' {
            *self.counts.entry(std::mem::take(&mut self.typed)).or_insert(0) += 1;
            return Vec::new();
        }
        self.typed.push(c);
        let mut m: Vec<(&String, u64)> = self.counts.iter().filter(|(s, _)| s.starts_with(self.typed.as_str())).map(|(s, &n)| (s, n)).collect();
        m.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(b.0)));
        m.into_iter().take(3).map(|(s, _)| s.clone()).collect()
    }
}
