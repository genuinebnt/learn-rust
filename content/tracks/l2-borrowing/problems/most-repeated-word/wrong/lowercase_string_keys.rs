use std::collections::HashMap;

pub fn top_words(text: &str, k: usize) -> Vec<(&str, usize)> {
    let mut counts: HashMap<String, (usize, usize, &str)> = HashMap::new();
    for (i, w) in text.split(|c: char| !c.is_alphanumeric()).filter(|w| !w.is_empty()).enumerate() {
        counts.entry(w.to_ascii_lowercase()).or_insert((0, i, w)).0 += 1;
    }
    let mut top: Vec<(usize, usize, &str)> = counts.into_values().collect();
    top.sort_unstable_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
    top.into_iter().take(k).map(|(n, _, w)| (w, n)).collect()
}
