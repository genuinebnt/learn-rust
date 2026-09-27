pub fn reverse_each_word(s: &str) -> String {
    s.split_whitespace()
        .map(|w| {
            let mut clusters: Vec<String> = Vec::new();
            for c in w.chars() {
                match clusters.last_mut() {
                    Some(last) if matches!(c, '\u{300}'..='\u{36f}') => last.push(c),
                    _ => clusters.push(c.to_string()),
                }
            }
            clusters.into_iter().rev().collect::<String>()
        })
        .collect::<Vec<_>>()
        .join(" ")
}
