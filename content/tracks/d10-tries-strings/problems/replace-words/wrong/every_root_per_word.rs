pub fn replace_words(roots: &[&str], sentence: &str) -> String {
    sentence
        .split(' ')
        .map(|w| roots.iter().filter(|r| w.starts_with(**r)).min_by_key(|r| r.len()).copied().unwrap_or(w))
        .collect::<Vec<&str>>()
        .join(" ")
}
