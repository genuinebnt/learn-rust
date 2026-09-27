/// The first word longer than `n`; otherwise pushes "fallback" and returns it.
pub fn first_long_or_push(words: &mut Vec<String>, n: usize) -> &String {
    if let Some(i) = words.iter().position(|w| w.len() > n) {
        return &words[i];
    }
    words.push("fallback".to_string());
    words.last().expect("just pushed")
}
