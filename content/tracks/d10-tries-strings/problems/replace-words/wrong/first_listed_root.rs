pub fn replace_words(roots: &[&str], sentence: &str) -> String {
    sentence
        .split(' ')
        .map(|w| roots.iter().find(|r| w.starts_with(**r)).copied().unwrap_or(w))
        .collect::<Vec<&str>>()
        .join(" ")
}
