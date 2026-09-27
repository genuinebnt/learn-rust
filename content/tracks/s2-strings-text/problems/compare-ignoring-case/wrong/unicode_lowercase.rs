pub fn is_command(input: &str, command: &str) -> bool {
    input.trim().to_lowercase() == command.to_lowercase()
}

pub fn count_word(text: &str, word: &str) -> usize {
    text.split_whitespace().filter(|w| w.to_lowercase() == word.to_lowercase()).count()
}
