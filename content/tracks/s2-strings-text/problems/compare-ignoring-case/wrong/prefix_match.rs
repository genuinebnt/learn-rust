pub fn is_command(input: &str, command: &str) -> bool {
    let input = input.trim();
    input.len() >= command.len() && input.as_bytes()[..command.len()].eq_ignore_ascii_case(command.as_bytes())
}

pub fn count_word(text: &str, word: &str) -> usize {
    text.split_whitespace().filter(|w| w.eq_ignore_ascii_case(word)).count()
}
