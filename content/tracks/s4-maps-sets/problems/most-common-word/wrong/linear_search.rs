pub fn most_common_word(paragraph: &str, banned: &[&str]) -> String {
    let mut counts: Vec<(String, usize)> = Vec::new();
    for w in paragraph.split(|c: char| !c.is_ascii_alphabetic()).filter(|w| !w.is_empty()) {
        let w = w.to_ascii_lowercase();
        if banned.contains(&w.as_str()) {
            continue;
        }
        match counts.iter_mut().find(|(k, _)| *k == w) {
            Some((_, c)) => *c += 1,
            None => counts.push((w, 1)),
        }
    }
    counts.into_iter().max_by(|a, b| a.1.cmp(&b.1).then_with(|| b.0.cmp(&a.0))).map(|(w, _)| w).unwrap_or_default()
}
