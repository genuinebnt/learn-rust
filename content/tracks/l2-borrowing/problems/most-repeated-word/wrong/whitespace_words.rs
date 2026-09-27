use std::collections::HashMap;
use std::hash::{Hash, Hasher};

/// A word that compares and hashes ignoring ASCII case.
struct Word<'a>(&'a str);

impl PartialEq for Word<'_> {
    fn eq(&self, other: &Self) -> bool {
        self.0.eq_ignore_ascii_case(other.0)
    }
}

impl Eq for Word<'_> {}

impl Hash for Word<'_> {
    fn hash<H: Hasher>(&self, state: &mut H) {
        for b in self.0.bytes() {
            state.write_u8(b.to_ascii_lowercase());
        }
        state.write_u8(0xff);
    }
}

pub fn top_words(text: &str, k: usize) -> Vec<(&str, usize)> {
    // word -> (count, index of its first appearance)
    let mut counts: HashMap<Word, (usize, usize)> = HashMap::new();
    for (i, w) in text.split_whitespace().enumerate() {
        counts.entry(Word(w)).or_insert((0, i)).0 += 1;
    }
    let mut top: Vec<(&str, usize, usize)> = counts.into_iter().map(|(w, (n, first))| (w.0, n, first)).collect();
    top.sort_unstable_by(|a, b| b.1.cmp(&a.1).then(a.2.cmp(&b.2)));
    top.into_iter().take(k).map(|(w, n, _)| (w, n)).collect()
}
