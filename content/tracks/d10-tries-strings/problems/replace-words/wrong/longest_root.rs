pub fn replace_words(roots: &[&str], sentence: &str) -> String {
    let mut sorted: Vec<&str> = roots.to_vec();
    sorted.sort_by_key(|r| std::cmp::Reverse(r.len()));
    sentence
        .split(' ')
        .map(|w| sorted.iter().find(|r| w.starts_with(**r)).copied().unwrap_or(w))
        .collect::<Vec<&str>>()
        .join(" ")
}
