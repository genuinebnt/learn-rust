pub fn most_repeated(text: &str) -> Option<&str> {
    let mut counts: Vec<(&str, usize)> = Vec::new();
    for w in text.split_whitespace() {
        match counts.iter_mut().find(|(k, _)| *k == w) {
            Some((_, c)) => *c += 1,
            None => counts.push((w, 1)),
        }
    }
    counts.into_iter().max_by(|a, b| a.1.cmp(&b.1).then_with(|| b.0.cmp(a.0))).map(|(w, _)| w)
}
